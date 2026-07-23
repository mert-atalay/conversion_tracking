"""Meta Conversions API payload helpers for CEFA parent CRM outcomes."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Mapping, Sequence
from urllib.request import Request, urlopen

from .config import ConsentState
from .models import require_granted_consent, require_sha256_hex
from .normalization import sha256_normalized_email, sha256_normalized_phone


META_DATASET_ID = "918227085392601"
DEFAULT_GRAPH_API_VERSION = "v22.0"
MAX_EVENT_AGE = timedelta(days=7)
CRM_STAGE_EVENT_NAMES = {
    "tour_scheduled": "CEFA_CRM_TourScheduled",
    "tour_completed_candidate": "CEFA_CRM_TourCompletedCandidate",
    "crm_closed_won": "CEFA_CRM_ClosedWon",
}
FORBIDDEN_EVENT_NAMES = frozenset({"Inquiry Submit"})
_META_COOKIE_RE = re.compile(r"^fb\.[12]\.[0-9]{1,20}\.[A-Za-z0-9_-]{1,512}$")

HttpTransport = Callable[[str, str, Mapping[str, str], Mapping[str, Any] | None], Mapping[str, Any]]


@dataclass(frozen=True)
class MetaMatchKeys:
    """Restricted match inputs at the dispatcher-to-adapter boundary."""

    email_sha256: str | None = None
    phone_sha256: str | None = None
    email_transient: str | None = None
    phone_transient: str | None = None
    external_id: str | None = None
    fbc: str | None = None
    fbp: str | None = None
    consent_state: ConsentState = ConsentState.UNKNOWN


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


def build_meta_event(
    outbox: Mapping[str, Any],
    keys: MetaMatchKeys,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build one approved CRM event and enforce Meta's seven-day event window."""

    require_granted_consent(keys.consent_state)
    canonical_stage = _required(outbox, "canonical_stage")
    if canonical_stage not in CRM_STAGE_EVENT_NAMES:
        raise ValueError(f"Unsupported Meta CRM stage: {canonical_stage}")
    event_timestamp = _parse_timestamp(_required(outbox, "event_timestamp", "stage_timestamp", "occurred_at"))
    comparison_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if event_timestamp > comparison_time:
        raise ValueError("Meta event timestamp cannot be in the future")
    if comparison_time - event_timestamp > MAX_EVENT_AGE:
        raise ValueError("Meta event is older than the seven-day dispatch window")
    external_id = require_sha256_hex(
        _required({"external_id": keys.external_id}, "external_id"),
        "external_id",
    )
    user_data: dict[str, Any] = {"external_id": [external_id]}
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
        user_data["em"] = [email_hash]
    if phone_hash:
        user_data["ph"] = [phone_hash]
    # fbc/fbp are passed through only when their values were captured upstream.
    fbc = _nonempty(keys.fbc)
    fbp = _nonempty(keys.fbp)
    if fbc:
        if not _META_COOKIE_RE.fullmatch(fbc):
            raise ValueError("fbc has an invalid captured-cookie format")
        user_data["fbc"] = fbc
    if fbp:
        if not _META_COOKIE_RE.fullmatch(fbp):
            raise ValueError("fbp has an invalid captured-cookie format")
        user_data["fbp"] = fbp
    if not any(key in user_data for key in ("em", "ph", "fbc", "fbp")):
        raise ValueError("Meta event needs a real match key beyond CEFA external_id")
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
