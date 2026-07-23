"""Google Data Manager payload and diagnostics helpers for parent CRM outcomes.

This module intentionally has no storage or scheduling responsibilities.  The
dispatcher supplies one already-eligible outbox record, restricted match keys,
and a destination registry entry for the canonical stage.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import urlencode
from urllib.request import Request, urlopen


GOOGLE_ADS_ACCOUNT_ID = "4159217891"
INGEST_EVENTS_URL = "https://datamanager.googleapis.com/v1/events:ingest"
REQUEST_STATUS_URL = "https://datamanager.googleapis.com/v1/requestStatus:retrieve"
GOOGLE_DESTINATION_TYPE = "GOOGLE_ADS"
DIAGNOSTIC_TERMINAL_STATUSES = frozenset({"SUCCESS", "FAILED", "PARTIAL_SUCCESS"})

HttpTransport = Callable[[str, str, Mapping[str, str], Mapping[str, Any] | None], Mapping[str, Any]]


@dataclass(frozen=True)
class GoogleDestination:
    """Registry-owned destination configuration for one approved CRM stage."""

    product_destination_id: str
    login_account_id: str | None = None
    login_account_type: str = GOOGLE_DESTINATION_TYPE


@dataclass(frozen=True)
class GoogleMatchKeys:
    """Restricted raw keys used only while building one upload request."""

    gclid: str | None = None
    gbraid: str | None = None
    wbraid: str | None = None
    email: str | None = None
    phone: str | None = None
    user_data_allowed: bool = False


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


def _rfc3339(value: object) -> str:
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
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_email(value: str) -> str:
    return value.strip().lower()


def normalize_phone(value: str) -> str:
    return "".join(character for character in value if character.isdigit())


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _user_identifiers(keys: GoogleMatchKeys) -> list[dict[str, str]]:
    if not keys.user_data_allowed:
        return []
    identifiers: list[dict[str, str]] = []
    email = _nonempty(keys.email)
    if email:
        identifiers.append({"emailAddress": sha256_hex(normalize_email(email))})
    phone = _nonempty(keys.phone)
    if phone:
        normalized_phone = normalize_phone(phone)
        if normalized_phone:
            identifiers.append({"phoneNumber": sha256_hex(normalized_phone)})
    return identifiers


def build_google_event(outbox: Mapping[str, Any], keys: GoogleMatchKeys) -> dict[str, Any]:
    """Build one CEFA parent CRM event without adding consent or fabricated IDs."""

    event: dict[str, Any] = {
        "eventTimestamp": _rfc3339(_required(outbox, "event_timestamp", "stage_timestamp", "occurred_at")),
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
        event["adIdentifiers"] = ad_identifiers
    identifiers = _user_identifiers(keys)
    if identifiers:
        event["userData"] = {"userIdentifiers": identifiers}
    if not ad_identifiers and not identifiers:
        raise ValueError("Google event needs a real click ID or approved user data")
    return event


def build_ingest_events_request(
    events: Sequence[Mapping[str, Any]],
    destination: GoogleDestination,
    *,
    validate_only: bool = True,
    consent: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an IngestEvents request for one configured Google Ads destination."""

    if not events:
        raise ValueError("IngestEvents requests require at least one event")
    product_destination_id = _nonempty(destination.product_destination_id)
    if not product_destination_id:
        raise ValueError("product_destination_id is required")
    account: dict[str, str] = {
        "accountType": GOOGLE_DESTINATION_TYPE,
        "accountId": GOOGLE_ADS_ACCOUNT_ID,
    }
    google_destination: dict[str, Any] = {
        "operatingAccount": account,
        "productDestinationId": product_destination_id,
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
    }
    if any("userData" in event for event in events):
        request["encoding"] = "HEX"
    # Consent is only forwarded when the caller has an approved interpretation.
    if consent is not None:
        request["consent"] = dict(consent)
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
    consent: Mapping[str, Any] | None = None,
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
        consent=consent,
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
