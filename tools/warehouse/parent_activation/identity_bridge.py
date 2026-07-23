"""PII-minimizing Form 4 identity capture and GreenRope matching.

Raw form and CRM contact values exist only in request memory. The durable
contract contains HMAC fingerprints, governed CEFA identifiers, public school
metadata, and explicit processing states.
"""

from __future__ import annotations

import csv
import hashlib
import hmac
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .greenrope_adapter import greenrope_opportunity_hmac, normalize_field_label
from .models import require_safe_opaque_id, require_sha256_hex
from .normalization import normalize_email, normalize_phone, normalize_text


FORM_ID = "4"
MATCH_WINDOW_SECONDS = 24 * 60 * 60
MIN_MATCH_SCORE = 4
IDENTITY_FIELD_NAMES = ("cefa_event_id", "cefa_form_entry_id")
_DATE_PATTERNS = (
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%Y%m%d",
)
_SAFE_ENTRY_ID_RE = re.compile(r"^[1-9][0-9]{0,19}$")


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def parse_datetime(value: object | None, field: str) -> datetime:
    text = normalize_text(value)
    if not text:
        raise ValueError(f"{field} is required")
    candidate = text.replace("Z", "+00:00")
    try:
        return _aware_utc(datetime.fromisoformat(candidate))
    except ValueError:
        pass
    for pattern in _DATE_PATTERNS:
        try:
            return _aware_utc(datetime.strptime(text, pattern))
        except ValueError:
            continue
    raise ValueError(f"{field} is invalid")


def _normalized_date_or_text(value: object | None) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    try:
        return parse_datetime(text, "date").date().isoformat()
    except ValueError:
        return " ".join(text.lower().split())


def _normalized_name(value: object | None) -> str:
    return " ".join(normalize_text(value).lower().split())


def _normalized_program(value: object | None) -> str:
    return " ".join(normalize_text(value).lower().split())


def identity_hmac(secret: bytes, namespace: str, value: str) -> str | None:
    normalized = value.strip()
    if not normalized:
        return None
    if not secret:
        raise ValueError("identity HMAC secret is required")
    message = f"cefa_parent_form4_identity_v1|{namespace}|{normalized}".encode("utf-8")
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def _fingerprint(secret: bytes, namespace: str, value: object | None) -> str | None:
    normalizers = {
        "assigned_email": lambda item: normalize_email(item),
        "assigned_phone": lambda item: normalize_phone(item),
        "parent_first": _normalized_name,
        "parent_last": _normalized_name,
        "child_dob": _normalized_date_or_text,
        "program": _normalized_program,
        "requested_start": _normalized_date_or_text,
    }
    return identity_hmac(secret, namespace, normalizers[namespace](value))


@dataclass(frozen=True, slots=True)
class SchoolBinding:
    school_uuid: str
    school_slug: str
    school_name: str
    greenrope_group_id: str


def load_school_bindings(path: Path) -> dict[str, SchoolBinding]:
    bindings: dict[str, SchoolBinding] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if str(row.get("status") or "").strip().lower() != "enabled":
                continue
            binding = SchoolBinding(
                school_uuid=require_safe_opaque_id(str(row["school_uuid"]), "school_uuid"),
                school_slug=require_safe_opaque_id(str(row["school_slug"]), "school_slug"),
                school_name=normalize_text(row["school_name"]),
                greenrope_group_id=require_safe_opaque_id(
                    str(row["greenrope_group_id"]),
                    "greenrope_group_id",
                ),
            )
            if binding.school_uuid in bindings:
                raise ValueError(f"duplicate school UUID in identity map: {binding.school_uuid}")
            bindings[binding.school_uuid] = binding
    if not bindings:
        raise ValueError("identity school map contains no enabled bindings")
    return bindings


def build_identity_record(
    payload: Mapping[str, Any],
    *,
    secret: bytes,
    school_bindings: Mapping[str, SchoolBinding],
    received_at: datetime,
) -> dict[str, Any]:
    """Validate a selected Form 4 payload and return its no-raw-PII record."""

    if str(payload.get("form_id") or "").strip() != FORM_ID:
        raise ValueError("unsupported form_id")
    entry_id = str(payload.get("entry_id") or "").strip()
    if not _SAFE_ENTRY_ID_RE.fullmatch(entry_id):
        raise ValueError("entry_id is invalid")
    event_id = require_safe_opaque_id(str(payload.get("event_id") or ""), "form4_event_id")
    school_uuid = require_safe_opaque_id(str(payload.get("school_uuid") or ""), "school_uuid")
    submitted_at = parse_datetime(payload.get("submitted_at"), "submitted_at")
    received = _aware_utc(received_at)
    binding = school_bindings.get(school_uuid)
    bridge_status = "captured" if binding else "quarantined"
    quarantine_reason = None if binding else "unknown_school_uuid"
    consent_signal = normalize_text(payload.get("consent"))
    record = {
        "form4_event_id": event_id,
        "form_entry_id": entry_id,
        "school_uuid": school_uuid,
        "greenrope_group_id": binding.greenrope_group_id if binding else None,
        "submitted_at": submitted_at.isoformat().replace("+00:00", "Z"),
        "assigned_email_hmac": _fingerprint(
            secret,
            "assigned_email",
            payload.get("email"),
        ),
        "assigned_phone_hmac": _fingerprint(
            secret,
            "assigned_phone",
            payload.get("phone"),
        ),
        "parent_first_hmac": _fingerprint(
            secret,
            "parent_first",
            payload.get("parent_first"),
        ),
        "parent_last_hmac": _fingerprint(
            secret,
            "parent_last",
            payload.get("parent_last"),
        ),
        "child_dob_hmac": _fingerprint(
            secret,
            "child_dob",
            payload.get("child_dob"),
        ),
        "program_hmac": _fingerprint(
            secret,
            "program",
            payload.get("program"),
        ),
        "requested_start_hmac": _fingerprint(
            secret,
            "requested_start",
            payload.get("requested_start"),
        ),
        "consent_signal_status": "present_unverified" if consent_signal else "unknown",
        "bridge_status": bridge_status,
        "candidate_count": 0,
        "match_score": None,
        "opportunity_id_hmac": None,
        "quarantine_reason": quarantine_reason,
        "greenrope_readback_confirmed": False,
        "attempt_count": 0,
        "last_attempt_at": None,
        "matched_at": None,
        "greenrope_written_at": None,
        "created_at": received.isoformat().replace("+00:00", "Z"),
        "updated_at": received.isoformat().replace("+00:00", "Z"),
    }
    for key, value in record.items():
        if key.endswith("_hmac") and value is not None:
            require_sha256_hex(str(value), key)
    return record


def _custom_fields(opportunity: Mapping[str, Any]) -> dict[str, str]:
    container = opportunity.get("customfields")
    raw = container.get("customfield") if isinstance(container, Mapping) else []
    rows = raw if isinstance(raw, list) else [raw] if isinstance(raw, Mapping) else []
    fields: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        label = normalize_field_label(row.get("fieldname") or row.get("name"))
        value = normalize_text(row.get("fieldvalue") or row.get("value"))
        if label and value:
            fields[label] = value
    return fields


def _first_value(mapping: Mapping[str, Any], *labels: str) -> str:
    normalized = {normalize_field_label(key): value for key, value in mapping.items()}
    for label in labels:
        value = normalize_text(normalized.get(normalize_field_label(label)))
        if value:
            return value
    return ""


def _field_value(fields: Mapping[str, str], *labels: str) -> str:
    for label in labels:
        value = normalize_text(fields.get(normalize_field_label(label)))
        if value:
            return value
    return ""


@dataclass(frozen=True, slots=True, repr=False)
class GreenRopeIdentityCandidate:
    raw_opportunity_id: str
    opportunity_id_hmac: str
    group_id: str
    created_at: datetime
    quality: str
    close_date: str
    assigned_email_hmac: str | None
    assigned_phone_hmac: str | None
    parent_first_hmac: str | None
    parent_last_hmac: str | None
    child_dob_hmac: str | None
    program_hmac: str | None
    requested_start_hmac: str | None
    current_event_id: str | None
    current_form_entry_id: str | None


def parse_greenrope_candidate(
    opportunity: Mapping[str, Any],
    *,
    group_id: str,
    secret: bytes,
) -> GreenRopeIdentityCandidate:
    raw_id = _first_value(opportunity, "opportunity_id", "opportunityid", "id")
    if not raw_id:
        raise ValueError("GreenRope opportunity is missing opportunity_id")
    fields = _custom_fields(opportunity)
    created_text = _first_value(
        opportunity,
        "createdate",
        "create_date",
        "created_at",
        "date_created",
        "created",
    )
    created_at = parse_datetime(created_text, "opportunity_created_at")
    assigned_email = _first_value(opportunity, "assignedtoemail")
    assigned_phone = _first_value(
        opportunity,
        "assignedtomobile",
        "assignedtophone",
        "assigned_to_mobile",
        "assigned_to_phone",
    )
    return GreenRopeIdentityCandidate(
        raw_opportunity_id=raw_id,
        opportunity_id_hmac=greenrope_opportunity_hmac(secret, raw_id),
        group_id=require_safe_opaque_id(group_id, "greenrope_group_id"),
        created_at=created_at,
        quality=_first_value(opportunity, "quality") or "0",
        close_date=_normalized_date_or_text(
            _first_value(opportunity, "closedate", "close_date")
        ).replace("-", ""),
        assigned_email_hmac=_fingerprint(secret, "assigned_email", assigned_email),
        assigned_phone_hmac=_fingerprint(secret, "assigned_phone", assigned_phone),
        parent_first_hmac=_fingerprint(
            secret,
            "parent_first",
            _first_value(opportunity, "assignedtofirstname"),
        ),
        parent_last_hmac=_fingerprint(
            secret,
            "parent_last",
            _first_value(opportunity, "assignedtolastname"),
        ),
        child_dob_hmac=_fingerprint(
            secret,
            "child_dob",
            _field_value(
                fields,
                "child_dob",
                "child_date_of_birth",
                "date_of_birth",
                "birthdate",
            ),
        ),
        program_hmac=_fingerprint(
            secret,
            "program",
            _field_value(fields, "program", "program_name"),
        ),
        requested_start_hmac=_fingerprint(
            secret,
            "requested_start",
            _field_value(
                fields,
                "requested_start",
                "requested_start_date",
                "start_date",
            ),
        ),
        current_event_id=_field_value(fields, "cefa_event_id") or None,
        current_form_entry_id=_field_value(fields, "cefa_form_entry_id") or None,
    )


@dataclass(frozen=True, slots=True)
class IdentityMatchDecision:
    status: str
    candidate: GreenRopeIdentityCandidate | None
    candidate_count: int
    match_score: int | None
    reason: str | None


_SCORE_FIELDS = (
    "assigned_phone_hmac",
    "parent_first_hmac",
    "parent_last_hmac",
    "child_dob_hmac",
    "program_hmac",
    "requested_start_hmac",
)


def select_identity_match(
    identity: Mapping[str, Any],
    candidates: Iterable[GreenRopeIdentityCandidate],
) -> IdentityMatchDecision:
    """Apply audited group + email + 24h + scored deterministic matching."""

    submitted_at = parse_datetime(identity.get("submitted_at"), "submitted_at")
    expected_email = identity.get("assigned_email_hmac")
    if not expected_email:
        return IdentityMatchDecision("quarantined", None, 0, None, "missing_email_identity")
    eligible = [
        candidate
        for candidate in candidates
        if candidate.group_id == str(identity.get("greenrope_group_id") or "")
        and candidate.assigned_email_hmac == expected_email
        and abs((candidate.created_at - submitted_at).total_seconds()) <= MATCH_WINDOW_SECONDS
    ]
    if not eligible:
        return IdentityMatchDecision("quarantined", None, 0, None, "no_candidate")
    scored: list[tuple[int, float, GreenRopeIdentityCandidate]] = []
    for candidate in eligible:
        score = sum(
            1
            for field in _SCORE_FIELDS
            if identity.get(field)
            and getattr(candidate, field)
            and identity.get(field) == getattr(candidate, field)
        )
        scored.append(
            (
                score,
                abs((candidate.created_at - submitted_at).total_seconds()),
                candidate,
            )
        )
    best_score = max(score for score, _, _ in scored)
    if best_score < MIN_MATCH_SCORE:
        return IdentityMatchDecision(
            "quarantined",
            None,
            len(eligible),
            best_score,
            "low_match_score",
        )
    best = [row for row in scored if row[0] == best_score]
    if len(best) == 1:
        return IdentityMatchDecision("matched", best[0][2], len(eligible), best_score, None)
    nearest_gap = min(gap for _, gap, _ in best)
    nearest = [row for row in best if row[1] == nearest_gap]
    if len(nearest) == 1:
        return IdentityMatchDecision(
            "matched",
            nearest[0][2],
            len(eligible),
            best_score,
            None,
        )
    return IdentityMatchDecision(
        "quarantined",
        None,
        len(eligible),
        best_score,
        "ambiguous_candidate",
    )
