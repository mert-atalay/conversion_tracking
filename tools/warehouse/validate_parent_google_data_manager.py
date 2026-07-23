#!/usr/bin/env python3
"""Validate CEFA parent CRM Google destinations without uploading conversions."""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.error
from datetime import datetime, timezone
from typing import Any

import google.auth
from google.auth.transport.requests import Request as GoogleAuthRequest

from parent_activation.config import ConsentState
from parent_activation.google_datamanager import (
    GoogleDestination,
    GoogleMatchKeys,
    build_google_event,
    ingest_google_events,
)


DATA_MANAGER_SCOPE = "https://www.googleapis.com/auth/datamanager"
DESTINATIONS = (
    ("CEFA | Parent | CRM Tour Scheduled | GOOGLE", "7695582127"),
    ("CEFA | Parent | CRM Tour Completed Candidate | GOOGLE", "7695186674"),
    ("CEFA | Parent | CRM Closed Won | GOOGLE", "7695186677"),
)


def _access_token() -> str:
    credentials, _ = google.auth.default(scopes=[DATA_MANAGER_SCOPE])
    credentials.refresh(GoogleAuthRequest())
    token = str(credentials.token or "").strip()
    if not token:
        raise RuntimeError("Google Data Manager access token was not issued")
    return token


def _validation_event(action_id: str, now: datetime) -> dict[str, Any]:
    transaction_id = hashlib.sha256(
        f"cefa-parent-data-manager-validation:{action_id}".encode("utf-8")
    ).hexdigest()
    return build_google_event(
        {
            "event_timestamp": now.isoformat(),
            "transaction_id": transaction_id,
        },
        GoogleMatchKeys(
            gclid=f"cefa-validation-only-{action_id}",
            click_id_captured_at=now,
            consent_state=ConsentState.GRANTED,
        ),
    )


def _safe_http_error(exc: urllib.error.HTTPError) -> dict[str, Any]:
    api_status = ""
    api_message = ""
    try:
        body = json.loads(exc.read().decode("utf-8"))
        error = body.get("error") if isinstance(body, dict) else {}
        if isinstance(error, dict):
            api_status = str(error.get("status") or "")
            api_message = str(error.get("message") or "")[:500]
    except (UnicodeDecodeError, json.JSONDecodeError):
        pass
    return {
        "http_status": exc.code,
        "api_status": api_status,
        "api_message": api_message,
    }


def main() -> int:
    now = datetime.now(timezone.utc)
    token = _access_token()
    results: list[dict[str, Any]] = []
    failures = 0
    for action_name, action_id in DESTINATIONS:
        event = _validation_event(action_id, now)
        try:
            result = ingest_google_events(
                [event],
                GoogleDestination(action_id),
                access_token=token,
                validate_only=True,
                consent_state=ConsentState.GRANTED,
            )
            results.append(
                {
                    "action_name": action_name,
                    "action_id": action_id,
                    "status": "validate_only_submitted",
                    "validate_only": result.validate_only,
                    "request_id": result.request_id,
                }
            )
        except urllib.error.HTTPError as exc:
            failures += 1
            results.append(
                {
                    "action_name": action_name,
                    "action_id": action_id,
                    "status": "validate_only_blocked",
                    **_safe_http_error(exc),
                }
            )
    print(json.dumps({"failures": failures, "results": results}, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(
            json.dumps(
                {
                    "failures": len(DESTINATIONS),
                    "status": "runtime_error",
                    "error_type": type(exc).__name__,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        raise SystemExit(1)
