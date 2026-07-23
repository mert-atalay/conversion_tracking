"""Google Data Manager payload and diagnostics helpers for parent CRM outcomes.

This module intentionally has no storage or scheduling responsibilities.  The
dispatcher supplies one already-eligible outbox record, restricted match keys,
and a destination registry entry for the canonical stage.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .config import ConsentState, GoogleConversionActionType
from .models import require_granted_consent, require_sha256_hex
from .normalization import (
    google_click_id_is_eligible,
    google_user_data_is_eligible,
    sha256_normalized_email,
    sha256_normalized_phone,
)


GOOGLE_ADS_ACCOUNT_ID = "4159217891"
INGEST_EVENTS_URL = "https://datamanager.googleapis.com/v1/events:ingest"
REQUEST_STATUS_URL = "https://datamanager.googleapis.com/v1/requestStatus:retrieve"
GOOGLE_DESTINATION_TYPE = "GOOGLE_ADS"
DIAGNOSTIC_TERMINAL_STATUSES = frozenset({"SUCCESS", "FAILED", "PARTIAL_SUCCESS"})
_NUMERIC_ID_RE = re.compile(r"^[1-9][0-9]{0,30}$")
_CLICK_ID_RE = re.compile(r"^[A-Za-z0-9_-]{5,512}$")

HttpTransport = Callable[[str, str, Mapping[str, str], Mapping[str, Any] | None], Mapping[str, Any]]


@dataclass(frozen=True)
class GoogleDestination:
    """Registry-owned destination configuration for one approved CRM stage."""

    conversion_action_id: str
    conversion_action_type: GoogleConversionActionType = GoogleConversionActionType.UPLOAD_CLICKS
    login_account_id: str | None = None
    login_account_type: str = GOOGLE_DESTINATION_TYPE

    def __post_init__(self) -> None:
        if not _NUMERIC_ID_RE.fullmatch(str(self.conversion_action_id).strip()):
            raise ValueError("Google conversion_action_id must be a bare numeric action ID")
        if self.conversion_action_type is not GoogleConversionActionType.UPLOAD_CLICKS:
            raise ValueError("Google destination must reference an UPLOAD_CLICKS conversion action")
        if self.login_account_id and not _NUMERIC_ID_RE.fullmatch(str(self.login_account_id).strip()):
            raise ValueError("Google login_account_id must be numeric")


@dataclass(frozen=True)
class GoogleMatchKeys:
    """Restricted keys consumed at the dispatcher-to-adapter boundary.

    SHA-256 values are the durable representation. Raw contact values are
    accepted only through explicitly transient fields and are normalized and
    hashed in memory. Capture timestamps are mandatory for any supplied key.
    """

    gclid: str | None = None
    gbraid: str | None = None
    wbraid: str | None = None
    click_id_captured_at: datetime | None = None
    email_sha256: str | None = None
    phone_sha256: str | None = None
    email_transient: str | None = None
    phone_transient: str | None = None
    user_data_captured_at: datetime | None = None
    consent_state: ConsentState = ConsentState.UNKNOWN


@dataclass(frozen=True)
class GoogleSendResult:
    request_id: str | None
    validate_only: bool
    response: Mapping[str, Any]


@dataclass(frozen=True)
class GoogleDiagnosticStatus:
    request_status: str
    normalized_status: str
    terminal: bool
    errors: tuple[Mapping[str, Any], ...]
    warnings: tuple[Mapping[str, Any], ...]
    record_count: int | None
    destination: Mapping[str, Any] | None


def _nonempty(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _required(mapping: Mapping[str, Any], *names: str) -> str:
    for name in names:
        value = _nonempty(mapping.get(name))
        if value:
            return value
    raise ValueError(f"Missing required value; expected one of {', '.join(names)}")


def _parse_timestamp(value: object) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("event timestamp must be ISO-8601/RFC3339") from exc
    else:
        raise ValueError("event timestamp must be ISO-8601/RFC3339")
    if parsed.tzinfo is None:
        raise ValueError("event timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def _rfc3339(value: object) -> str:
    return _parse_timestamp(value).isoformat().replace("+00:00", "Z")


def _user_identifiers(keys: GoogleMatchKeys) -> list[dict[str, str]]:
    identifiers: list[dict[str, str]] = []
    if keys.email_sha256 and keys.email_transient:
        raise ValueError("provide either email_sha256 or email_transient, never both")
    if keys.phone_sha256 and keys.phone_transient:
        raise ValueError("provide either phone_sha256 or phone_transient, never both")
    email_hash = (
        require_sha256_hex(keys.email_sha256, "email_sha256")
        if keys.email_sha256
        else sha256_normalized_email(keys.email_transient)
    )
    phone_hash = (
        require_sha256_hex(keys.phone_sha256, "phone_sha256")
        if keys.phone_sha256
        else sha256_normalized_phone(keys.phone_transient)
    )
    if email_hash:
        identifiers.append({"emailAddress": email_hash})
    if phone_hash:
        identifiers.append({"phoneNumber": phone_hash})
    return identifiers


def build_google_event(outbox: Mapping[str, Any], keys: GoogleMatchKeys) -> dict[str, Any]:
    """Build one eligible event after fail-closed consent and age checks."""

    require_granted_consent(keys.consent_state)
    event_timestamp = _parse_timestamp(_required(outbox, "event_timestamp"))
    event: dict[str, Any] = {
        "eventTimestamp": _rfc3339(event_timestamp),
        "transactionId": _required(outbox, "platform_transaction_id", "transaction_id"),
        "eventSource": "WEB",
    }
    ad_identifiers = {
        key: value
        for key, value in {
            "gclid": _nonempty(keys.gclid),
            "gbraid": _nonempty(keys.gbraid),
            "wbraid": _nonempty(keys.wbraid),
        }.items()
        if value
    }
    if ad_identifiers:
        if keys.click_id_captured_at is None:
            raise ValueError("click_id_captured_at is required for Google click identifiers")
        if not google_click_id_is_eligible(keys.click_id_captured_at, event_timestamp):
            raise ValueError("Google click identifier is outside the permitted age window")
        for name, value in ad_identifiers.items():
            if not _CLICK_ID_RE.fullmatch(value):
                raise ValueError(f"{name} has an invalid identifier format")
        event["adIdentifiers"] = ad_identifiers
    identifiers = _user_identifiers(keys)
    if identifiers:
        if keys.user_data_captured_at is None:
            raise ValueError("user_data_captured_at is required for Google enhanced lead matching")
        if not google_user_data_is_eligible(keys.user_data_captured_at, event_timestamp):
            raise ValueError("Google enhanced lead identifier is outside the permitted age window")
        event["userData"] = {"userIdentifiers": identifiers}
    if not ad_identifiers and not identifiers:
        raise ValueError("Google event needs an eligible real click ID or consented user data")
    return event


def build_ingest_events_request(
    events: Sequence[Mapping[str, Any]],
    destination: GoogleDestination,
    *,
    validate_only: bool = True,
    consent_state: ConsentState = ConsentState.UNKNOWN,
) -> dict[str, Any]:
    """Build an IngestEvents request for one configured Google Ads destination."""

    if not events:
        raise ValueError("IngestEvents requests require at least one event")
    require_granted_consent(consent_state)
    account: dict[str, str] = {
        "accountType": GOOGLE_DESTINATION_TYPE,
        "accountId": GOOGLE_ADS_ACCOUNT_ID,
    }
    google_destination: dict[str, Any] = {
        "operatingAccount": account,
        "productDestinationId": destination.conversion_action_id,
    }
    login_account_id = _nonempty(destination.login_account_id)
    if login_account_id:
        google_destination["loginAccount"] = {
            "accountType": _nonempty(destination.login_account_type) or GOOGLE_DESTINATION_TYPE,
            "accountId": login_account_id,
        }
    request: dict[str, Any] = {
        "destinations": [google_destination],
        "events": [dict(event) for event in events],
        "validateOnly": validate_only,
        "consent": {"adUserData": "CONSENT_GRANTED"},
    }
    if any("userData" in event for event in events):
        request["encoding"] = "HEX"
    return request


def _urllib_transport(
    method: str,
    url: str,
    headers: Mapping[str, str],
    payload: Mapping[str, Any] | None,
) -> Mapping[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(url, data=body, headers=dict(headers), method=method)
    with urlopen(request, timeout=90) as response:
        return json.loads(response.read().decode("utf-8"))


def send_ingest_events(
    request: Mapping[str, Any],
    *,
    access_token: str,
    transport: HttpTransport = _urllib_transport,
) -> GoogleSendResult:
    """Send a ready IngestEvents request and return its persisted request ID."""

    token = _nonempty(access_token)
    if not token:
        raise ValueError("Google Data Manager access token is required")
    response = transport(
        "POST",
        INGEST_EVENTS_URL,
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        request,
    )
    request_id = _nonempty(response.get("requestId"))
    return GoogleSendResult(
        request_id=request_id,
        validate_only=bool(request.get("validateOnly")),
        response=response,
    )


def ingest_google_events(
    events: Sequence[Mapping[str, Any]],
    destination: GoogleDestination,
    *,
    access_token: str,
    validate_only: bool = True,
    consent_state: ConsentState = ConsentState.UNKNOWN,
    transport: HttpTransport = _urllib_transport,
) -> GoogleSendResult:
    """Build and submit one configured Google destination batch.

    ``validate_only`` deliberately defaults to true.  The dispatcher must opt
    into a real upload only after its platform eligibility checks have passed.
    """

    request = build_ingest_events_request(
        events,
        destination,
        validate_only=validate_only,
        consent_state=consent_state,
    )
    return send_ingest_events(request, access_token=access_token, transport=transport)


def normalize_diagnostics_status(response: Mapping[str, Any]) -> list[GoogleDiagnosticStatus]:
    """Reduce Google diagnostics to stable dispatcher-facing delivery states."""

    statuses: list[GoogleDiagnosticStatus] = []
    for item in response.get("requestStatusPerDestination", []):
        if not isinstance(item, Mapping):
            continue
        raw_status = _nonempty(item.get("requestStatus")) or "REQUEST_STATUS_UNKNOWN"
        normalized = {
            "SUCCESS": "accepted",
            "PARTIAL_SUCCESS": "partial_failure",
            "FAILED": "failed",
            "PROCESSING": "processing",
        }.get(raw_status, "unknown")
        events_status = item.get("eventsIngestionStatus")
        record_count: int | None = None
        if isinstance(events_status, Mapping):
            try:
                record_count = int(events_status["recordCount"])
            except (KeyError, TypeError, ValueError):
                pass
        error_info = item.get("errorInfo")
        warning_info = item.get("warningInfo")
        errors = tuple(error_info.get("errorCounts", [])) if isinstance(error_info, Mapping) else ()
        warnings = tuple(warning_info.get("warningCounts", [])) if isinstance(warning_info, Mapping) else ()
        destination = item.get("destination")
        statuses.append(
            GoogleDiagnosticStatus(
                request_status=raw_status,
                normalized_status=normalized,
                terminal=raw_status in DIAGNOSTIC_TERMINAL_STATUSES,
                errors=errors,
                warnings=warnings,
                record_count=record_count,
                destination=destination if isinstance(destination, Mapping) else None,
            )
        )
    return statuses


def retrieve_request_status(
    request_id: str,
    *,
    access_token: str,
    transport: HttpTransport = _urllib_transport,
) -> list[GoogleDiagnosticStatus]:
    """Retrieve and normalize Data Manager delivery diagnostics for a request."""

    normalized_request_id = _nonempty(request_id)
    token = _nonempty(access_token)
    if not normalized_request_id:
        raise ValueError("request_id is required")
    if not token:
        raise ValueError("Google Data Manager access token is required")
    url = f"{REQUEST_STATUS_URL}?{urlencode({'requestId': normalized_request_id})}"
    response = transport("GET", url, {"Authorization": f"Bearer {token}"}, None)
    return normalize_diagnostics_status(response)


def retrieve_google_status(
    request_id: str,
    *,
    access_token: str,
    transport: HttpTransport = _urllib_transport,
) -> list[GoogleDiagnosticStatus]:
    """Dispatcher-facing alias for normalized Data Manager diagnostics."""

    return retrieve_request_status(request_id, access_token=access_token, transport=transport)
