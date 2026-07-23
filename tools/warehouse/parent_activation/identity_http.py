"""Secret-authenticated HTTP boundary for the Form 4 identity bridge."""

from __future__ import annotations

import hmac
import json
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping, Protocol

from .identity_bridge import build_identity_record, load_school_bindings


MAX_REQUEST_BYTES = 16 * 1024
WEBHOOK_PATH = "/gravity-forms/form-4"


class IdentityStore(Protocol):
    def upsert_identity(self, record: Mapping[str, Any]) -> None: ...


def process_webhook(
    *,
    headers: Mapping[str, str],
    body: bytes,
    webhook_secret: str,
    identity_secret: bytes,
    school_map_path: Path,
    store: IdentityStore,
    received_at: datetime | None = None,
) -> tuple[int, dict[str, object]]:
    """Return a generic response without reflecting payload data."""

    supplied = str(headers.get("X-CEFA-Identity-Secret") or "")
    if not webhook_secret or not hmac.compare_digest(supplied, webhook_secret):
        return HTTPStatus.UNAUTHORIZED, {"status": "unauthorized"}
    if not body or len(body) > MAX_REQUEST_BYTES:
        return HTTPStatus.BAD_REQUEST, {"status": "invalid_request"}
    try:
        payload = json.loads(body.decode("utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError("payload must be an object")
        record = build_identity_record(
            payload,
            secret=identity_secret,
            school_bindings=load_school_bindings(school_map_path),
            received_at=received_at or datetime.now(timezone.utc),
        )
        store.upsert_identity(record)
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return HTTPStatus.BAD_REQUEST, {"status": "invalid_request"}
    return HTTPStatus.ACCEPTED, {"status": "accepted"}


class IdentityBridgeHandler(BaseHTTPRequestHandler):
    """Low-volume Cloud Run handler with payload logging disabled."""

    server_version = "CEFAIdentityBridge/1.0"

    def log_message(self, _: str, *args: object) -> None:
        return

    def _write_json(self, status: int, payload: Mapping[str, object]) -> None:
        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler contract.
        if self.path != "/healthz":
            self._write_json(HTTPStatus.NOT_FOUND, {"status": "not_found"})
            return
        self._write_json(HTTPStatus.OK, {"status": "healthy"})

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler contract.
        if self.path != WEBHOOK_PATH:
            self._write_json(HTTPStatus.NOT_FOUND, {"status": "not_found"})
            return
        try:
            content_length = int(self.headers.get("Content-Length") or "0")
        except ValueError:
            content_length = 0
        if not 0 < content_length <= MAX_REQUEST_BYTES:
            self._write_json(HTTPStatus.BAD_REQUEST, {"status": "invalid_request"})
            return
        body = self.rfile.read(content_length)
        status, response = process_webhook(
            headers=dict(self.headers.items()),
            body=body,
            webhook_secret=self.server.webhook_secret,
            identity_secret=self.server.identity_secret,
            school_map_path=self.server.school_map_path,
            store=self.server.identity_store,
        )
        self._write_json(status, response)


class IdentityBridgeServer(ThreadingHTTPServer):
    webhook_secret: str
    identity_secret: bytes
    school_map_path: Path
    identity_store: IdentityStore


def run_server(
    *,
    host: str,
    port: int,
    webhook_secret: str,
    identity_secret: bytes,
    school_map_path: Path,
    store: IdentityStore,
) -> None:
    server = IdentityBridgeServer((host, port), IdentityBridgeHandler)
    server.webhook_secret = webhook_secret
    server.identity_secret = identity_secret
    server.school_map_path = school_map_path
    server.identity_store = store
    server.serve_forever()
