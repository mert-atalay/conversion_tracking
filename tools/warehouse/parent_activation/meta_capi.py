"""Meta Conversions API payload helpers for CEFA parent CRM outcomes."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Mapping, Sequence
from urllib.request import Request, urlopen


META_DATASET_ID = "918227085392601"
DEFAULT_GRAPH_API_VERSION = "v22.0"
MAX_EVENT_AGE = timedelta(days=7)
CRM_STAGE_EVENT_NAMES = {
    "tour_scheduled": "CEFA_CRM_TourScheduled",
    "tour_completed_candidate": "CEFA_CRM_TourCompletedCandidate",
    "crm_closed_won": "CEFA_CRM_ClosedWon",
}
FORBIDDEN_EVENT_NAMES = frozenset({"Inquiry Submit"})

HttpTransport = Callable[[str, str, Mapping[str, str], Mapping[str, Any] | None], Mapping[str, Any]]


@dataclass(frozen=True)
class MetaMatchKeys:
    """Restricted raw match inputs; values are never returned in an event payload."""

    email: str | None = None
    phone: str | None = None
    external_id: str | None = None
    fbc: str | None = None
    fbp: str | None = None
    user_data_allowed: bool = False


@dataclass(frozen=True)
class MetaSendResult:
    events_received: int | None
    messages: tuple[Mapping[str, Any], ...]
    trace_id: str | None
    response: Mapping[str, Any]


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


def normalize_email(value: str) -> str:
    return value.strip().lower()


def normalize_phone(value: str) -> str:
    return "".join(character for character in value if character.isdigit())


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_meta_event(
    outbox: Mapping[str, Any],
    keys: MetaMatchKeys,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build one approved CRM event and enforce Meta's seven-day event window."""

    canonical_stage = _required(outbox, "canonical_stage")
    if canonical_stage not in CRM_STAGE_EVENT_NAMES:
        raise ValueError(f"Unsupported Meta CRM stage: {canonical_stage}")
    event_timestamp = _parse_timestamp(_required(outbox, "event_timestamp", "stage_timestamp", "occurred_at"))
    comparison_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if event_timestamp > comparison_time:
        raise ValueError("Meta event timestamp cannot be in the future")
    if comparison_time - event_timestamp > MAX_EVENT_AGE:
        raise ValueError("Meta event is older than the seven-day dispatch window")
    external_id = _required({"external_id": keys.external_id}, "external_id")
    user_data: dict[str, Any] = {"external_id": [external_id]}
    if keys.user_data_allowed:
        email = _nonempty(keys.email)
        if email:
            user_data["em"] = [sha256_hex(normalize_email(email))]
        phone = _nonempty(keys.phone)
        if phone:
            normalized_phone = normalize_phone(phone)
            if normalized_phone:
                user_data["ph"] = [sha256_hex(normalized_phone)]
    # fbc/fbp are passed through only when their values were captured upstream.
    fbc = _nonempty(keys.fbc)
    fbp = _nonempty(keys.fbp)
    if fbc:
        user_data["fbc"] = fbc
    if fbp:
        user_data["fbp"] = fbp
    return {
        "event_name": CRM_STAGE_EVENT_NAMES[canonical_stage],
        "event_time": int(event_timestamp.timestamp()),
        "event_id": _required(outbox, "platform_transaction_id", "transaction_id"),
        "action_source": "system_generated",
        "user_data": user_data,
        "custom_data": {
            "cefa_canonical_stage": canonical_stage,
            "school_uuid": _required(outbox, "school_uuid"),
            "source_system": _nonempty(outbox.get("source_system")) or "greenrope",
        },
    }


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


def send_meta_events(
    events: Sequence[Mapping[str, Any]],
    *,
    access_token: str,
    test_event_code: str | None = None,
    api_version: str = DEFAULT_GRAPH_API_VERSION,
    transport: HttpTransport = _urllib_transport,
) -> MetaSendResult:
    """Send CRM events to the governed parent dataset through injectable HTTP."""

    if not events:
        raise ValueError("Meta CAPI requests require at least one event")
    for event in events:
        event_name = _nonempty(event.get("event_name"))
        if event_name in FORBIDDEN_EVENT_NAMES or event_name not in CRM_STAGE_EVENT_NAMES.values():
            raise ValueError("This adapter only sends approved CEFA CRM events")
    token = _nonempty(access_token)
    version = _nonempty(api_version)
    if not token:
        raise ValueError("Meta CAPI access token is required")
    if not version:
        raise ValueError("Meta Graph API version is required")
    payload: dict[str, Any] = {"data": [dict(event) for event in events]}
    test_code = _nonempty(test_event_code)
    if test_code:
        payload["test_event_code"] = test_code
    response = transport(
        "POST",
        f"https://graph.facebook.com/{version}/{META_DATASET_ID}/events",
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        payload,
    )
    events_received: int | None = None
    try:
        events_received = int(response["events_received"])
    except (KeyError, TypeError, ValueError):
        pass
    messages = response.get("messages", [])
    return MetaSendResult(
        events_received=events_received,
        messages=tuple(message for message in messages if isinstance(message, Mapping)),
        trace_id=_nonempty(response.get("fbtrace_id")),
        response=response,
    )
