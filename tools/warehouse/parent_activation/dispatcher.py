"""Idempotent dispatcher for approved parent CRM outcome events."""

from __future__ import annotations

import hashlib
import os
import re
import socket
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

from .bigquery_store import ParentActivationBigQueryStore
from .config import ConsentState
from .google_datamanager import (
    GoogleDestination,
    GoogleMatchKeys,
    build_google_event,
    ingest_google_events,
    retrieve_google_status,
)
from .meta_capi import MetaMatchKeys, build_meta_event, send_meta_events
from .models import require_safe_opaque_id
from .repository import ParentActivationRepository


DATA_MANAGER_SCOPE = "https://www.googleapis.com/auth/datamanager"
ALLOWED_MODES = frozenset(
    {"disabled", "dry_run", "validate_only", "test", "secondary_production"}
)
RETRY_DELAYS = (
    timedelta(minutes=5),
    timedelta(minutes=15),
    timedelta(hours=1),
    timedelta(hours=6),
    timedelta(hours=24),
)


@dataclass(frozen=True, slots=True)
class DispatchSummary:
    mode: str
    inspected: int
    leased: int
    accepted: int
    processing: int
    validated: int
    tested: int
    retried: int
    failed: int
    skipped: int

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "inspected": self.inspected,
            "leased": self.leased,
            "accepted": self.accepted,
            "processing": self.processing,
            "validated": self.validated,
            "tested": self.tested,
            "retried": self.retried,
            "failed": self.failed,
            "skipped": self.skipped,
        }


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _mode(value: str | None) -> str:
    normalized = str(value or "disabled").strip().lower()
    if normalized not in ALLOWED_MODES:
        raise ValueError(f"unsupported PARENT_ACTIVATION_MODE: {normalized}")
    return normalized


def _timestamp(value: object | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("restricted match-key timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def _consent(value: object | None) -> ConsentState:
    try:
        return ConsentState(str(value or "unknown").strip().lower())
    except ValueError as exc:
        raise ValueError("invalid restricted consent state") from exc


def _google_access_token() -> str:
    import google.auth
    from google.auth.transport.requests import Request as GoogleAuthRequest

    credentials, _ = google.auth.default(scopes=[DATA_MANAGER_SCOPE])
    credentials.refresh(GoogleAuthRequest())
    token = str(credentials.token or "").strip()
    if not token:
        raise RuntimeError("Google Data Manager access token was not issued")
    return token


def _worker_id() -> str:
    basis = f"{socket.gethostname()}|{os.getpid()}|{uuid.uuid4()}"
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def _retry_at(attempt_count: int, now: datetime) -> datetime:
    index = min(max(attempt_count - 1, 0), len(RETRY_DELAYS) - 1)
    return now + RETRY_DELAYS[index]


def _error_code(value: object) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_.:-]+", "_", str(value)).strip("_")
    return require_safe_opaque_id((normalized or "runtime_error")[:80], "error_code")


def _attempt_row(
    row: Mapping[str, Any],
    *,
    status: str,
    started_at: datetime,
    finished_at: datetime,
    request_id: str | None = None,
    platform_event_id: str | None = None,
    retryable: bool | None = None,
    error_code: str | None = None,
    error_message: str | None = None,
    warning_count: int = 0,
    accepted_at: datetime | None = None,
) -> dict[str, Any]:
    return {
        "delivery_attempt_id": str(uuid.uuid4()),
        "outbox_id": row["outbox_id"],
        "transaction_id": row["transaction_id"],
        "platform": row["platform"],
        "destination_action_key": row["destination_action_key"],
        "attempt_number": int(row.get("attempt_count") or 0) + 1,
        "attempt_started_at": started_at.isoformat(),
        "attempt_finished_at": finished_at.isoformat(),
        "delivery_status": status,
        "response_status_code": None,
        "request_id": request_id,
        "platform_event_id": platform_event_id,
        "is_retryable": retryable,
        "error_code": error_code,
        "error_message": error_message,
        "warning_count": warning_count,
        "accepted_at": accepted_at.isoformat() if accepted_at else None,
        "created_at": finished_at.isoformat(),
    }


def _google_keys(match: Mapping[str, Any]) -> GoogleMatchKeys:
    return GoogleMatchKeys(
        gclid=match.get("gclid"),
        gbraid=match.get("gbraid"),
        wbraid=match.get("wbraid"),
        click_id_captured_at=_timestamp(match.get("click_id_captured_at")),
        email_sha256=match.get("email_sha256"),
        phone_sha256=match.get("phone_sha256"),
        user_data_captured_at=_timestamp(match.get("user_data_captured_at")),
        consent_state=_consent(match.get("consent_status")),
    )


def _meta_keys(row: Mapping[str, Any], match: Mapping[str, Any]) -> MetaMatchKeys:
    return MetaMatchKeys(
        email_sha256=match.get("email_sha256"),
        phone_sha256=match.get("phone_sha256"),
        external_id=row.get("activation_subject_id_hmac"),
        fbc=match.get("fbc"),
        fbp=match.get("fbp"),
        consent_state=_consent(match.get("consent_status")),
    )


def _platform_enabled(platform: str, mode: str) -> bool:
    if mode == "dry_run":
        return True
    if platform == "google":
        return _truthy(os.environ.get("GOOGLE_OFFLINE_UPLOAD_ENABLED"))
    if platform == "meta":
        return _truthy(os.environ.get("META_CRM_CAPI_ENABLED"))
    return False


def dispatch_due(
    *,
    repository: ParentActivationRepository,
    store: ParentActivationBigQueryStore,
    mode: str | None = None,
    google_access_token: str | None = None,
    meta_access_token: str | None = None,
    meta_test_event_code: str | None = None,
    now: datetime | None = None,
    limit: int = 100,
) -> DispatchSummary:
    runtime_mode = _mode(mode if mode is not None else os.environ.get("PARENT_ACTIVATION_MODE"))
    if runtime_mode == "disabled":
        return DispatchSummary(runtime_mode, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    current_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    worker_id = _worker_id()
    counters = {
        "inspected": 0,
        "leased": 0,
        "accepted": 0,
        "processing": 0,
        "validated": 0,
        "tested": 0,
        "retried": 0,
        "failed": 0,
        "skipped": 0,
    }
    google_token = google_access_token
    meta_token = meta_access_token or os.environ.get("META_ACCESS_TOKEN")
    test_code = meta_test_event_code or os.environ.get("META_TEST_EVENT_CODE")

    for row in repository.due_outbox_rows(limit=limit):
        counters["inspected"] += 1
        platform = str(row.get("platform") or "").lower()
        if row.get("activation_mode") != runtime_mode:
            counters["skipped"] += 1
            continue
        if not _platform_enabled(platform, runtime_mode):
            counters["skipped"] += 1
            continue
        if runtime_mode in {"validate_only", "test"} and platform == "meta" and not test_code:
            counters["skipped"] += 1
            continue
        outbox_id = require_safe_opaque_id(str(row["outbox_id"]), "outbox_id")
        if not store.lease_outbox(outbox_id, worker_id, lease_seconds=900):
            counters["skipped"] += 1
            continue
        counters["leased"] += 1
        started = datetime.now(timezone.utc)
        try:
            match = repository.match_key(str(row["form4_event_id"]))
            if match is None:
                raise ValueError("missing_or_expired_match_key")

            if runtime_mode == "dry_run":
                store.record_delivery_attempt(
                    _attempt_row(
                        row,
                        status="dry_run_ready",
                        started_at=started,
                        finished_at=datetime.now(timezone.utc),
                    )
                )
                store.release_lease(outbox_id, worker_id)
                counters["validated"] += 1
                continue

            if platform == "google":
                if google_token is None:
                    google_token = _google_access_token()
                event = build_google_event(row, _google_keys(match))
                validate_only = runtime_mode != "secondary_production"
                result = ingest_google_events(
                    [event],
                    GoogleDestination(str(row["destination_action_key"])),
                    access_token=google_token,
                    validate_only=validate_only,
                    consent_state=_consent(match.get("consent_status")),
                )
                if not result.request_id:
                    raise RuntimeError("google_request_id_missing")
                finished = datetime.now(timezone.utc)
                status = "validate_only_pass" if validate_only else "processing"
                store.record_delivery_attempt(
                    _attempt_row(
                        row,
                        status=status,
                        started_at=started,
                        finished_at=finished,
                        request_id=result.request_id,
                    )
                )
                if validate_only:
                    store.mark_nonproduction_pass(
                        outbox_id,
                        worker_id,
                        delivery_status="validate_only_pass",
                    )
                    counters["validated"] += 1
                else:
                    store.mark_processing(
                        outbox_id,
                        worker_id,
                        request_id=result.request_id,
                    )
                    counters["processing"] += 1
                continue

            if platform == "meta":
                if not meta_token:
                    raise RuntimeError("meta_access_token_missing")
                event = build_meta_event(row, _meta_keys(row, match), now=current_time)
                is_test = runtime_mode in {"validate_only", "test"}
                result = send_meta_events(
                    [event],
                    access_token=meta_token,
                    test_event_code=test_code if is_test else None,
                )
                if result.events_received != 1:
                    raise RuntimeError("meta_event_not_received")
                finished = datetime.now(timezone.utc)
                status = "test_accepted" if is_test else "accepted"
                store.record_delivery_attempt(
                    _attempt_row(
                        row,
                        status=status,
                        started_at=started,
                        finished_at=finished,
                        platform_event_id=str(result.trace_id or row["transaction_id"]),
                        warning_count=len(result.messages),
                        accepted_at=None if is_test else finished,
                    )
                )
                if is_test:
                    store.mark_nonproduction_pass(
                        outbox_id,
                        worker_id,
                        delivery_status="test_accepted",
                    )
                    counters["tested"] += 1
                else:
                    store.mark_accepted(
                        outbox_id,
                        worker_id,
                        str(row["transaction_id"]),
                    )
                    counters["accepted"] += 1
                continue

            raise ValueError("unsupported_platform")
        except ValueError as exc:
            finished = datetime.now(timezone.utc)
            error_code = _error_code(exc)
            store.record_delivery_attempt(
                _attempt_row(
                    row,
                    status="permanent_failure",
                    started_at=started,
                    finished_at=finished,
                    retryable=False,
                    error_code=error_code,
                )
            )
            store.mark_permanent_failure(
                outbox_id,
                worker_id,
                error_code=error_code,
                error_message=None,
            )
            counters["failed"] += 1
        except Exception as exc:  # Network/platform failures are retried without logging response bodies.
            finished = datetime.now(timezone.utc)
            attempt_count = int(row.get("attempt_count") or 0) + 1
            retryable = attempt_count < len(RETRY_DELAYS)
            error_code = _error_code(f"runtime_{type(exc).__name__}")
            store.record_delivery_attempt(
                _attempt_row(
                    row,
                    status="retryable_failure" if retryable else "permanent_failure",
                    started_at=started,
                    finished_at=finished,
                    retryable=retryable,
                    error_code=error_code,
                )
            )
            if retryable:
                store.mark_retryable_failure(
                    outbox_id,
                    worker_id,
                    error_code=error_code,
                    error_message=None,
                    next_attempt_at=_retry_at(attempt_count, current_time),
                )
                counters["retried"] += 1
            else:
                store.mark_permanent_failure(
                    outbox_id,
                    worker_id,
                    error_code=error_code,
                    error_message=None,
                )
                counters["failed"] += 1

    return DispatchSummary(runtime_mode, **counters)


def refresh_google_diagnostics(
    *,
    repository: ParentActivationRepository,
    store: ParentActivationBigQueryStore,
    google_access_token: str | None = None,
    now: datetime | None = None,
    limit: int = 100,
) -> dict[str, int]:
    current_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    token = google_access_token or _google_access_token()
    summary = {"inspected": 0, "accepted": 0, "processing": 0, "retried": 0, "failed": 0}
    for row in repository.processing_google_rows(limit=limit):
        summary["inspected"] += 1
        request_id = require_safe_opaque_id(str(row["request_id"]), "request_id")
        statuses = retrieve_google_status(request_id, access_token=token)
        if not statuses or any(not item.terminal for item in statuses):
            summary["processing"] += 1
            continue
        if all(item.normalized_status == "accepted" for item in statuses):
            if store.mark_diagnostic_accepted(
                str(row["outbox_id"]),
                request_id=request_id,
                accepted_lock_id=str(row["transaction_id"]),
            ):
                summary["accepted"] += 1
            continue
        attempt_count = int(row.get("attempt_count") or 0)
        retryable = attempt_count < len(RETRY_DELAYS)
        if store.mark_diagnostic_failure(
            str(row["outbox_id"]),
            request_id=request_id,
            retryable=retryable,
            error_code="google_delivery_failed",
            error_message=None,
            next_attempt_at=_retry_at(attempt_count, current_time) if retryable else None,
        ):
            summary["retried" if retryable else "failed"] += 1
    return summary
