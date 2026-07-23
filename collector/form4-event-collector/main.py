"""CEFA Form 4 no-PII event collector for Cloud Run."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import time
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from google.cloud import bigquery


PROJECT_ID = os.environ.get("BQ_PROJECT_ID", "marketing-api-488017")
TABLE_ID = os.environ.get(
    "BQ_TABLE_ID",
    "marketing-api-488017.raw_website_forms.form4_event_audit",
)
COLLECTOR_SECRET = os.environ.get("CEFA_COLLECTOR_SECRET", "").strip()
COLLECTOR_VERSION = os.environ.get("COLLECTOR_VERSION", "form4_event_collector_v1")
MAX_BODY_BYTES = int(os.environ.get("MAX_BODY_BYTES", "65536"))
MAX_SIGNATURE_AGE_SECONDS = int(os.environ.get("MAX_SIGNATURE_AGE_SECONDS", "900"))

EVENT_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")
CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")

STRING_LIMITS = {
    "event_id": 128,
    "event_name": 80,
    "form_id": 20,
    "form_family": 80,
    "lead_type": 80,
    "lead_intent": 80,
    "school_selected_id": 120,
    "school_selected_slug": 180,
    "school_selected_name": 220,
    "program_id": 80,
    "program_name": 220,
    "days_per_week": 120,
    "utm_source": 220,
    "utm_medium": 220,
    "utm_campaign": 300,
    "utm_term": 220,
    "utm_content": 300,
    "gclid": 300,
    "gbraid": 300,
    "wbraid": 300,
    "fbclid": 300,
    "msclkid": 300,
    "tracking_source": 80,
    "page_context": 80,
}

URL_FIELDS = {
    "first_landing_page": "first_landing_page_path",
    "first_referrer": "first_referrer_path",
    "event_source_url": "event_source_url_path",
    "inquiry_success_url": "inquiry_success_url_path",
}

ALLOWED_PAYLOAD_FIELDS = set(STRING_LIMITS) | set(URL_FIELDS) | {
    "event",
    "event_timestamp",
    "submitted_at",
    "inquiry_success",
    "test_mode",
}

BIGQUERY_CLIENT = bigquery.Client(project=PROJECT_ID)


def utc_now() -> datetime:
    """Return the current UTC datetime."""

    return datetime.now(timezone.utc)


def json_response(handler: BaseHTTPRequestHandler, status: HTTPStatus, payload: dict[str, Any]) -> None:
    """Write a compact JSON response."""

    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    handler.send_response(status.value)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def clean_text(value: Any, limit: int = 220) -> str | None:
    """Return a bounded plain-text value or None."""

    if value is None:
        return None
    cleaned = CONTROL_CHARS.sub("", str(value)).strip()
    if not cleaned:
        return None
    return cleaned[:limit]


def clean_url_path(value: Any) -> str | None:
    """Return a URL host/path without query string or fragment."""

    text = clean_text(value, 1000)
    if not text:
        return None
    parsed = urlparse(text)
    if parsed.scheme and parsed.netloc:
        path = parsed.path or "/"
        return f"{parsed.scheme.lower()}://{parsed.netloc.lower()}{path}"[:1000]
    if text.startswith("/"):
        return text.split("?", 1)[0].split("#", 1)[0][:1000]
    return None


def parse_timestamp(value: Any) -> str | None:
    """Parse an ISO-ish timestamp and return an RFC3339 string for BigQuery."""

    text = clean_text(value, 80)
    if not text:
        return None
    normalized = text.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat()


def event_date(timestamp_text: str | None, received_at: datetime) -> str:
    """Return event date from event timestamp or receive time."""

    if timestamp_text:
        try:
            return datetime.fromisoformat(timestamp_text).date().isoformat()
        except ValueError:
            pass
    return received_at.date().isoformat()


def verify_signature(headers: Any, body: bytes) -> tuple[bool, str]:
    """Verify timestamped HMAC signature."""

    if not COLLECTOR_SECRET:
        return False, "collector_secret_missing"

    timestamp = headers.get("X-CEFA-Timestamp", "")
    signature = headers.get("X-CEFA-Signature", "")
    if not timestamp or not signature.startswith("sha256="):
        return False, "signature_header_missing"

    try:
        timestamp_int = int(timestamp)
    except ValueError:
        return False, "timestamp_invalid"

    if abs(int(time.time()) - timestamp_int) > MAX_SIGNATURE_AGE_SECONDS:
        return False, "timestamp_outside_tolerance"

    expected = hmac.new(
        COLLECTOR_SECRET.encode("utf-8"),
        timestamp.encode("utf-8") + b"." + body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(f"sha256={expected}", signature):
        return False, "signature_invalid"

    return True, "valid"


def build_row(payload: dict[str, Any], body: bytes, request_id: str, received_at: datetime) -> dict[str, Any]:
    """Build an allowlisted BigQuery row."""

    event_id = clean_text(payload.get("event_id"), STRING_LIMITS["event_id"])
    if not event_id or not EVENT_ID_PATTERN.match(event_id):
        raise ValueError("event_id_missing_or_invalid")

    form_id = clean_text(payload.get("form_id"), STRING_LIMITS["form_id"])
    event_name = clean_text(payload.get("event"), STRING_LIMITS["event_name"])
    if form_id != "4" or event_name != "school_inquiry_submit":
        raise ValueError("unsupported_event_contract")

    event_timestamp = parse_timestamp(payload.get("event_timestamp") or payload.get("submitted_at"))

    row: dict[str, Any] = {
        "received_at": received_at.isoformat(),
        "request_id": request_id,
        "collector_version": COLLECTOR_VERSION,
        "event_id": event_id,
        "event_timestamp": event_timestamp,
        "event_date": event_date(event_timestamp, received_at),
        "event_name": event_name,
        "collector_status": "accepted",
        "signature_status": "valid",
        "pii_redacted": True,
        "is_test_event": bool(payload.get("test_mode")),
        "payload_hash": hashlib.sha256(body).hexdigest(),
        "source_status": "collector_active",
        "inserted_at": utc_now().isoformat(),
    }

    for field, limit in STRING_LIMITS.items():
        if field in {"event_id", "event_name"}:
            continue
        row[field] = clean_text(payload.get(field), limit)

    for payload_key, row_key in URL_FIELDS.items():
        row[row_key] = clean_url_path(payload.get(payload_key))

    return row


class CollectorHandler(BaseHTTPRequestHandler):
    """HTTP handler for Form 4 collector requests."""

    server_version = "CEFAForm4Collector/1.0"

    def do_GET(self) -> None:  # noqa: N802
        if self.path in {"/", "/healthz"}:
            json_response(self, HTTPStatus.OK, {"status": "ok", "collector": COLLECTOR_VERSION})
            return
        json_response(self, HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/collect/form4":
            json_response(self, HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            json_response(self, HTTPStatus.BAD_REQUEST, {"error": "invalid_content_length"})
            return

        if content_length <= 0 or content_length > MAX_BODY_BYTES:
            json_response(self, HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "invalid_body_size"})
            return

        body = self.rfile.read(content_length)
        signature_ok, signature_status = verify_signature(self.headers, body)
        if not signature_ok:
            json_response(self, HTTPStatus.UNAUTHORIZED, {"error": signature_status})
            return

        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            json_response(self, HTTPStatus.BAD_REQUEST, {"error": "invalid_json"})
            return

        if not isinstance(payload, dict):
            json_response(self, HTTPStatus.BAD_REQUEST, {"error": "invalid_payload"})
            return

        unknown_fields = set(payload) - ALLOWED_PAYLOAD_FIELDS
        if unknown_fields:
            json_response(
                self,
                HTTPStatus.BAD_REQUEST,
                {"error": "unsupported_fields", "fields": sorted(unknown_fields)},
            )
            return

        request_id = str(uuid.uuid4())
        received_at = utc_now()
        try:
            row = build_row(payload, body, request_id, received_at)
        except ValueError as exc:
            json_response(self, HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return

        errors = BIGQUERY_CLIENT.insert_rows_json(
            TABLE_ID,
            [row],
            row_ids=[row["event_id"]],
        )
        if errors:
            json_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "bigquery_insert_failed"})
            return

        json_response(self, HTTPStatus.ACCEPTED, {"status": "accepted", "request_id": request_id})

    def log_message(self, format_string: str, *args: Any) -> None:
        """Use the default stderr logger without request bodies."""

        super().log_message(format_string, *args)


def main() -> None:
    """Start the HTTP server."""

    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), CollectorHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
