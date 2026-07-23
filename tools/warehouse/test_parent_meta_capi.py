#!/usr/bin/env python3
"""Send synthetic CEFA parent CRM events to Meta Test Events only."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.error
from datetime import datetime, timezone
from typing import Any

from parent_activation.config import CanonicalStage, ConsentState
from parent_activation.meta_capi import (
    MetaMatchKeys,
    build_meta_event,
    send_meta_events,
)


TEST_SCHOOL_UUID = "00000000-0000-0000-0000-000000000000"
TEST_EMAIL_HASH = hashlib.sha256(
    b"cefa-parent-crm-test-only@invalid.example"
).hexdigest()
TEST_EXTERNAL_ID = hashlib.sha256(b"cefa-parent-crm-meta-test-only").hexdigest()


def _safe_http_error(exc: urllib.error.HTTPError) -> dict[str, Any]:
    api_code: int | None = None
    api_subcode: int | None = None
    api_type = ""
    try:
        body = json.loads(exc.read().decode("utf-8"))
        error = body.get("error") if isinstance(body, dict) else {}
        if isinstance(error, dict):
            api_code = error.get("code")
            api_subcode = error.get("error_subcode")
            api_type = str(error.get("type") or "")
    except (UnicodeDecodeError, json.JSONDecodeError):
        pass
    return {
        "http_status": exc.code,
        "api_code": api_code,
        "api_subcode": api_subcode,
        "api_type": api_type,
    }


def main() -> int:
    token = os.getenv("META_ACCESS_TOKEN", "").strip()
    test_code = os.getenv("META_TEST_EVENT_CODE", "").strip()
    if not token:
        raise RuntimeError("META_ACCESS_TOKEN is required")
    if not test_code.startswith("TEST") or len(test_code) < 8:
        raise RuntimeError("META_TEST_EVENT_CODE must be a Meta TEST code")

    now = datetime.now(timezone.utc).replace(microsecond=0)
    events: list[dict[str, Any]] = []
    for stage in CanonicalStage:
        event_id = hashlib.sha256(
            f"cefa-parent-meta-test:{stage.value}:{now.date()}".encode("utf-8")
        ).hexdigest()
        events.append(
            build_meta_event(
                {
                    "canonical_stage": stage.value,
                    "event_timestamp": now.isoformat(),
                    "transaction_id": event_id,
                    "school_uuid": TEST_SCHOOL_UUID,
                    "source_system": "cefa_test_events",
                },
                MetaMatchKeys(
                    email_sha256=TEST_EMAIL_HASH,
                    external_id=TEST_EXTERNAL_ID,
                    consent_state=ConsentState.GRANTED,
                ),
                now=now,
            )
        )

    try:
        result = send_meta_events(
            events,
            access_token=token,
            test_event_code=test_code,
        )
    except urllib.error.HTTPError as exc:
        print(
            json.dumps(
                {
                    "status": "meta_test_events_blocked",
                    "event_count": len(events),
                    **_safe_http_error(exc),
                },
                sort_keys=True,
            )
        )
        return 1

    print(
        json.dumps(
            {
                "status": "meta_test_events_submitted",
                "event_names": [event["event_name"] for event in events],
                "events_received": result.events_received,
                "message_count": len(result.messages),
                "trace_id": result.trace_id,
                "test_event_code_present": True,
                "synthetic_identity_only": True,
            },
            sort_keys=True,
        )
    )
    return 0 if result.events_received == len(events) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "runtime_error",
                    "error_type": type(exc).__name__,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        raise SystemExit(1)
