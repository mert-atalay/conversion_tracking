"""Read-only GreenRope adapter for prospective parent CRM lifecycle polling.

The adapter deliberately separates raw API parsing from durable lifecycle
records.  Contact values are normalized and hashed immediately; raw contact
values never appear in returned lifecycle records.  Click IDs/cookies are kept
only in transient ``PlatformMatchValues`` for a restricted downstream match-key
writer and must never be written to stdout or application logs.
"""

from __future__ import annotations

import concurrent.futures as futures
import hashlib
import hmac
import json
import random
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import escape
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import Form4Identity
from .normalization import normalize_email, normalize_phone, normalize_text, sha256_hex


DEFAULT_ENDPOINT = "https://api.stgi.net/api-xml"
REQUIRED_IDENTITY_FIELD_NAMES = frozenset({"cefaeventid", "cefaformentryid"})
RECOMMENDED_ATTRIBUTION_FIELD_NAMES = frozenset(
    {
        "utmsource",
        "utmmedium",
        "utmcampaign",
        "utmterm",
        "utmcontent",
        "gclid",
        "gbraid",
        "wbraid",
        "fbclid",
        "fbc",
        "fbp",
    }
)
_LABEL_RE = re.compile(r"[^a-z0-9]+")


def normalize_field_label(value: object | None) -> str:
    """Normalize GreenRope labels without depending on UI punctuation."""

    return _LABEL_RE.sub("", normalize_text(value).lower())


def _as_list(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [value]
    return []


def _find_envelope(payload: Mapping[str, Any], needle: str) -> Mapping[str, Any]:
    for key, value in payload.items():
        if needle in str(key).lower() and isinstance(value, Mapping):
            return value
    return {}


def _walk_mappings(value: object) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        yield value
        for child in value.values():
            yield from _walk_mappings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_mappings(child)


def _first(mapping: Mapping[str, Any], *names: str) -> str | None:
    normalized = {normalize_field_label(key): value for key, value in mapping.items()}
    for name in names:
        value = normalize_text(normalized.get(normalize_field_label(name)))
        if value:
            return value
    return None


def _custom_fields(opportunity: Mapping[str, Any]) -> dict[str, str]:
    raw = opportunity.get("customfields")
    rows = _as_list(raw.get("customfield")) if isinstance(raw, Mapping) else []
    fields: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        label = normalize_field_label(_first(row, "fieldname", "name", "key"))
        value = _first(row, "fieldvalue", "value")
        if label and value:
            fields[label] = value
    return fields


def _field_value(fields: Mapping[str, str], *labels: str) -> str | None:
    for label in labels:
        value = normalize_text(fields.get(normalize_field_label(label)))
        if value:
            return value
    return None


def _opportunity_phase(opportunity: Mapping[str, Any], fields: Mapping[str, str]) -> str | None:
    return _first(opportunity, "phase", "stage", "status") or _field_value(fields, "phase", "stage", "status")


def _hmac_identifier(secret: bytes | str, namespace: str, raw_value: str) -> str:
    if not secret:
        raise ValueError("PARENT_ACTIVATION_HMAC_SECRET is required")
    key = secret.encode("utf-8") if isinstance(secret, str) else secret
    message = f"cefa_parent_activation_v1|{namespace}|{raw_value}".encode("utf-8")
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def greenrope_opportunity_hmac(secret: bytes | str, raw_opportunity_id: str) -> str:
    """Return the canonical lifecycle HMAC for a native GreenRope ID."""

    return _hmac_identifier(secret, "greenrope_opportunity", raw_opportunity_id)


@dataclass(frozen=True, slots=True)
class FieldDefinition:
    field_id: str | None
    label: str
    normalized_label: str
    field_type: str | None
    active: str | None


@dataclass(frozen=True, slots=True)
class FieldReadiness:
    status: str
    present: frozenset[str]
    missing: frozenset[str]
    recommended_missing: frozenset[str]

    def to_safe_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "present": sorted(self.present),
            "missing": sorted(self.missing),
            "recommended_missing": sorted(self.recommended_missing),
        }


@dataclass(frozen=True, slots=True)
class PhaseDefinition:
    phase_id: str | None
    label: str
    normalized_label: str
    active: str | None


@dataclass(frozen=True, slots=True)
class PhasePathDefinition:
    path_id: str | None
    from_phase_id: str | None
    to_phase_id: str | None
    from_label: str | None
    to_label: str | None
    active: str | None


@dataclass(frozen=True, slots=True)
class PlatformMatchValues:
    """Transient restricted match values. Never serialize or log this object."""

    email_sha256: str | None
    phone_sha256: str | None
    gclid: str | None
    gbraid: str | None
    wbraid: str | None
    fbclid: str | None
    fbc: str | None
    fbp: str | None


@dataclass(frozen=True, slots=True)
class ParsedOpportunity:
    """Redacted lifecycle input plus transient platform matching material."""

    opportunity_id_hmac: str
    group_id: str
    raw_phase: str | None
    form4_event_id: str | None
    form_entry_id: str | None
    school_uuid: str | None
    utm_source: str | None
    utm_medium: str | None
    utm_campaign: str | None
    utm_term: str | None
    utm_content: str | None
    match_values: PlatformMatchValues

    def state_record(self) -> dict[str, str | None]:
        """Return the durable no-PII, no-click-ID state needed for comparisons."""

        return {
            "opportunity_id_hmac": self.opportunity_id_hmac,
            "group_id": self.group_id,
            "raw_phase": self.raw_phase,
            "form4_event_id": self.form4_event_id,
            "form_entry_id": self.form_entry_id,
            "school_uuid": self.school_uuid,
        }


@dataclass(frozen=True, slots=True)
class PollObservation:
    opportunity: ParsedOpportunity
    observed_at: datetime
    is_initial_baseline: bool
    phase_changed: bool

    def to_safe_dict(self) -> dict[str, object]:
        record = self.opportunity.state_record()
        record.update(
            {
                "observed_at": self.observed_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                "is_initial_baseline": self.is_initial_baseline,
                "phase_changed": self.phase_changed,
            }
        )
        return record


def evaluate_required_fields(field_labels: Iterable[str]) -> FieldReadiness:
    present = frozenset(normalize_field_label(label) for label in field_labels if normalize_field_label(label))
    missing = REQUIRED_IDENTITY_FIELD_NAMES.difference(present)
    return FieldReadiness(
        status="ready" if not missing else "blocked",
        present=present,
        missing=frozenset(missing),
        recommended_missing=frozenset(RECOMMENDED_ATTRIBUTION_FIELD_NAMES.difference(present)),
    )


def parse_field_dictionary(payload: Mapping[str, Any]) -> list[FieldDefinition]:
    """Extract only dictionary metadata from a GetOpportunityFields response."""

    definitions: dict[tuple[str | None, str], FieldDefinition] = {}
    for row in _walk_mappings(_find_envelope(payload, "getopportunityfieldsresponse") or payload):
        field_id = _first(row, "field_id", "fieldid")
        label = _first(row, "fieldname", "field_name", "name", "label")
        if not field_id or not label:
            continue
        normalized = normalize_field_label(label)
        if not normalized:
            continue
        definition = FieldDefinition(
            field_id=field_id,
            label=label,
            normalized_label=normalized,
            field_type=_first(row, "fieldtype", "field_type", "type"),
            active=_first(row, "active", "isactive", "status"),
        )
        definitions[(field_id, normalized)] = definition
    return sorted(definitions.values(), key=lambda item: (item.normalized_label, item.field_id or ""))


def parse_phase_dictionary(payload: Mapping[str, Any]) -> list[PhaseDefinition]:
    definitions: dict[tuple[str | None, str], PhaseDefinition] = {}
    for row in _walk_mappings(_find_envelope(payload, "getphasesresponse") or payload):
        phase_id = _first(row, "phase_id", "phaseid")
        label = _first(row, "phasename", "phase_name", "name", "label")
        if not phase_id or not label:
            continue
        normalized = normalize_field_label(label)
        if normalized:
            definitions[(phase_id, normalized)] = PhaseDefinition(
                phase_id=phase_id,
                label=label,
                normalized_label=normalized,
                active=_first(row, "active", "isactive", "status"),
            )
    return sorted(definitions.values(), key=lambda item: (item.normalized_label, item.phase_id or ""))


def parse_phase_paths(payload: Mapping[str, Any]) -> list[PhasePathDefinition]:
    definitions: dict[tuple[str | None, str | None, str | None], PhasePathDefinition] = {}
    for row in _walk_mappings(_find_envelope(payload, "getphasepathsresponse") or payload):
        path_id = _first(row, "phase_path_id", "phasepathid", "path_id")
        from_phase_id = _first(row, "from_phase_id", "fromphaseid", "source_phase_id")
        to_phase_id = _first(row, "to_phase_id", "tophaseid", "target_phase_id")
        if not path_id and not (from_phase_id and to_phase_id):
            continue
        definitions[(path_id, from_phase_id, to_phase_id)] = PhasePathDefinition(
            path_id=path_id,
            from_phase_id=from_phase_id,
            to_phase_id=to_phase_id,
            from_label=_first(row, "from_phase_name", "fromphasename", "source_phase_name"),
            to_label=_first(row, "to_phase_name", "tophasename", "target_phase_name"),
            active=_first(row, "active", "isactive", "status"),
        )
    return sorted(definitions.values(), key=lambda item: (item.path_id or "", item.from_phase_id or ""))


def parse_opportunity(
    opportunity: Mapping[str, Any],
    *,
    group_id: str,
    hmac_secret: bytes | str,
) -> ParsedOpportunity:
    """Parse a GreenRope opportunity without returning raw contact values."""

    raw_opportunity_id = _first(opportunity, "opportunity_id", "opportunityid", "id")
    if not raw_opportunity_id:
        raise ValueError("GreenRope opportunity is missing opportunity_id")
    fields = _custom_fields(opportunity)
    email = _field_value(fields, "email", "parentemail") or _first(opportunity, "email", "contactemail")
    phone = _field_value(fields, "phone", "parentphone", "mobilephone") or _first(opportunity, "phone", "mobilephone")
    match_values = PlatformMatchValues(
        email_sha256=sha256_hex(normalize_email(email)) if normalize_email(email) else None,
        phone_sha256=sha256_hex(normalize_phone(phone)) if normalize_phone(phone) else None,
        gclid=_field_value(fields, "gclid"),
        gbraid=_field_value(fields, "gbraid"),
        wbraid=_field_value(fields, "wbraid"),
        fbclid=_field_value(fields, "fbclid"),
        fbc=_field_value(fields, "fbc"),
        fbp=_field_value(fields, "fbp"),
    )
    return ParsedOpportunity(
        opportunity_id_hmac=greenrope_opportunity_hmac(
            hmac_secret,
            raw_opportunity_id,
        ),
        group_id=group_id,
        raw_phase=_opportunity_phase(opportunity, fields),
        form4_event_id=_field_value(fields, "cefa_event_id", "cefaeventid"),
        form_entry_id=_field_value(fields, "cefa_form_entry_id", "cefaformentryid"),
        school_uuid=_field_value(fields, "school_uuid", "schooluuid"),
        utm_source=_field_value(fields, "utm_source", "utmsource"),
        utm_medium=_field_value(fields, "utm_medium", "utmmedium"),
        utm_campaign=_field_value(fields, "utm_campaign", "utmcampaign"),
        utm_term=_field_value(fields, "utm_term", "utmterm"),
        utm_content=_field_value(fields, "utm_content", "utmcontent"),
        match_values=match_values,
    )


def as_unresolved_form4_identity(opportunity: ParsedOpportunity) -> Form4Identity:
    """Expose CRM identifiers to the core without pretending a BQ match exists."""

    return Form4Identity(
        event_id=opportunity.form4_event_id,
        form_entry_id=opportunity.form_entry_id,
        matched_event_id=None,
        matched_form_entry_id=None,
        match_count=0,
    )


def compare_to_previous(
    opportunities: Iterable[ParsedOpportunity],
    previous_state: Mapping[str, Mapping[str, Any]],
    *,
    observed_at: datetime,
    baseline: bool,
) -> list[PollObservation]:
    """Return baseline rows or prospective phase-change observations only."""

    if observed_at.tzinfo is None:
        raise ValueError("observed_at must be timezone-aware")
    observations: list[PollObservation] = []
    for opportunity in opportunities:
        prior = previous_state.get(opportunity.opportunity_id_hmac)
        changed = bool(prior and normalize_text(prior.get("raw_phase")) != normalize_text(opportunity.raw_phase))
        if baseline or prior is None or changed:
            observations.append(
                PollObservation(
                    opportunity=opportunity,
                    observed_at=observed_at,
                    is_initial_baseline=baseline or prior is None,
                    phase_changed=changed and not baseline,
                )
            )
    return observations


class GreenRopeClient:
    """Small GreenRope XML client limited to read-only request types."""

    def __init__(
        self,
        endpoint: str,
        email: str,
        token: str,
        account_id: str,
        timeout: int = 120,
        *,
        sleep: Callable[[float], None] = time.sleep,
        transport: Callable[[Request, int], Mapping[str, Any]] | None = None,
    ) -> None:
        self.endpoint = endpoint
        self.email = email
        self.token = token
        self.account_id = account_id
        self.timeout = timeout
        self._sleep = sleep
        self._transport = transport

    def call(self, xml: str) -> dict[str, Any]:
        body = urlencode({"email": self.email, "auth_token": self.token, "xml": xml}).encode("utf-8")
        request = Request(
            self.endpoint,
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": "cefa-parent-lifecycle-poller/1.0",
            },
            method="POST",
        )
        for attempt in range(4):
            try:
                if self._transport is not None:
                    payload = dict(self._transport(request, self.timeout))
                else:
                    with urlopen(request, timeout=self.timeout) as response:
                        payload = json.loads(response.read().decode("utf-8"))
                if not isinstance(payload, dict):
                    raise RuntimeError("GreenRope returned a non-object response")
                return payload
            except HTTPError as exc:
                if exc.code not in {429, 500, 502, 503, 504} or attempt == 3:
                    raise RuntimeError(f"GreenRope read request failed with HTTP {exc.code}") from exc
            except (TimeoutError, URLError) as exc:
                if attempt == 3:
                    raise RuntimeError(f"GreenRope read request failed: {type(exc).__name__}") from exc
            self._sleep((2**attempt) + random.uniform(0, 0.25))
        raise RuntimeError("GreenRope read request failed")

    def _request(self, name: str, **attributes: str) -> dict[str, Any]:
        rendered = " ".join(f'{key}="{escape(value, quote=True)}"' for key, value in attributes.items())
        return self.call(f"<{name} {rendered}></{name}>")

    def groups(self) -> list[dict[str, str]]:
        payload = self._request("GetGroupsRequest", account_id=self.account_id, response="json")
        envelope = _find_envelope(payload, "getgroupsresponse")
        rows = envelope.get("groups", {}).get("group") if isinstance(envelope.get("groups"), Mapping) else envelope.get("group")
        groups: list[dict[str, str]] = []
        for row in _as_list(rows):
            if not isinstance(row, Mapping):
                continue
            group_id = _first(row, "group_id", "groupid", "id")
            if group_id:
                groups.append({"id": group_id, "name": _first(row, "name", "groupname") or ""})
        return groups

    def opportunities(self, group_id: str) -> list[dict[str, Any]]:
        payload = self._request(
            "GetOpportunitiesRequest", account_id=self.account_id, group_id=group_id, response="json"
        )
        envelope = _find_envelope(payload, "getopportunitiesresponse")
        rows = envelope.get("opportunities", {}).get("opportunity") if isinstance(envelope.get("opportunities"), Mapping) else envelope.get("opportunity")
        return [dict(row) for row in _as_list(rows) if isinstance(row, Mapping)]

    def opportunity_fields(self) -> list[FieldDefinition]:
        return parse_field_dictionary(self._request("GetOpportunityFieldsRequest", account_id=self.account_id, response="json"))

    def phases(self) -> list[PhaseDefinition]:
        return parse_phase_dictionary(self._request("GetPhasesRequest", account_id=self.account_id, response="json"))

    def phase_paths(self) -> list[PhasePathDefinition]:
        return parse_phase_paths(self._request("GetPhasePathsRequest", account_id=self.account_id, response="json"))


def fetch_group_opportunities(
    client: GreenRopeClient,
    groups: Iterable[Mapping[str, str]],
    *,
    max_workers: int = 4,
) -> tuple[list[tuple[str, list[dict[str, Any]]]], list[dict[str, str]]]:
    """Fetch all group opportunities with the contractual four-request cap."""

    if not 1 <= max_workers <= 4:
        raise ValueError("max_workers must be between 1 and 4")
    successes: list[tuple[str, list[dict[str, Any]]]] = []
    errors: list[dict[str, str]] = []
    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        submitted = {executor.submit(client.opportunities, group["id"]): group["id"] for group in groups}
        for future in futures.as_completed(submitted):
            group_id = submitted[future]
            try:
                successes.append((group_id, future.result()))
            except Exception as exc:
                errors.append({"group_id": group_id, "error_type": type(exc).__name__})
    return successes, errors


def safe_dictionary_snapshot(client: GreenRopeClient) -> dict[str, object]:
    fields = client.opportunity_fields()
    phases = client.phases()
    paths = client.phase_paths()
    readiness = evaluate_required_fields(field.normalized_label for field in fields)
    return {
        "readiness": readiness.to_safe_dict(),
        "fields": [asdict(field) for field in fields],
        "phases": [asdict(phase) for phase in phases],
        "phase_paths": [asdict(path) for path in paths],
    }
