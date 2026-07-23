"""Prospective Gravity Forms Form 4 capture without an inbound webhook."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .identity_bridge import (
    SchoolBinding,
    build_identity_record,
    parse_datetime,
)


FORM_ID = "4"
PAGE_SIZE = 100
MAX_PAGES = 10
OVERLAP = timedelta(hours=1)


class IdentityStore(Protocol):
    def upsert_identity(self, record: Mapping[str, Any]) -> None: ...

    def latest_submitted_at(self) -> datetime | None: ...


class GravityFormsClient(Protocol):
    def entries(self, *, page: int, page_size: int) -> list[dict[str, Any]]: ...


class WordPressGravityFormsClient:
    """Read selected Form 4 entries over the authenticated GF REST API."""

    def __init__(
        self,
        *,
        site_url: str,
        username: str,
        application_password: str,
        timeout: int = 60,
    ) -> None:
        self.site_url = site_url.rstrip("/")
        self.timeout = timeout
        credential = base64.b64encode(
            f"{username}:{application_password}".encode("utf-8")
        ).decode("ascii")
        self.authorization = f"Basic {credential}"

    def entries(self, *, page: int, page_size: int) -> list[dict[str, Any]]:
        if page < 1 or not 1 <= page_size <= 500:
            raise ValueError("invalid Gravity Forms paging")
        query = urlencode(
            {
                "paging[page_size]": str(page_size),
                "paging[current_page]": str(page),
                "sorting[key]": "date_created",
                "sorting[direction]": "DESC",
            }
        )
        request = Request(
            f"{self.site_url}/wp-json/gf/v2/forms/{FORM_ID}/entries?{query}",
            headers={
                "Authorization": self.authorization,
                "Accept": "application/json",
                "User-Agent": "cefa-parent-form4-identity-capture/1.0",
            },
        )
        with urlopen(request, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        rows = payload.get("entries") if isinstance(payload, Mapping) else None
        if not isinstance(rows, list):
            raise RuntimeError("Gravity Forms returned an invalid entry response")
        return [dict(row) for row in rows if isinstance(row, Mapping)]


@dataclass(frozen=True, slots=True)
class CaptureRunResult:
    activation_start: str
    capture_floor: str
    entries_observed: int
    identities_upserted: int
    invalid_entries: int
    pages_read: int

    def to_dict(self) -> dict[str, object]:
        return {
            "activation_start": self.activation_start,
            "capture_floor": self.capture_floor,
            "entries_observed": self.entries_observed,
            "identities_upserted": self.identities_upserted,
            "invalid_entries": self.invalid_entries,
            "pages_read": self.pages_read,
        }


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _entry_payload(entry: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "form_id": str(entry.get("form_id") or FORM_ID),
        "entry_id": entry.get("id"),
        "submitted_at": entry.get("date_created"),
        "event_id": entry.get("32.4"),
        "school_uuid": entry.get("32.1"),
        "school_slug": entry.get("32.5"),
        "school_name": entry.get("32.6"),
        "parent_first": entry.get("4.3"),
        "parent_last": entry.get("5.6"),
        "email": entry.get("6"),
        "phone": entry.get("7"),
        "child_dob": entry.get("26"),
        "program": entry.get("32.7"),
        "requested_start": entry.get("49"),
        "consent": entry.get("56.1"),
    }


def capture_new_form4_identities(
    *,
    client: GravityFormsClient,
    store: IdentityStore,
    identity_secret: bytes,
    school_bindings: Mapping[str, SchoolBinding],
    activation_start: datetime,
    observed_at: datetime,
    page_size: int = PAGE_SIZE,
    max_pages: int = MAX_PAGES,
) -> CaptureRunResult:
    activation = _utc(activation_start)
    now = _utc(observed_at)
    latest = store.latest_submitted_at()
    floor = max(
        activation,
        _utc(latest) - OVERLAP if latest is not None else activation,
    )
    observed = 0
    upserted = 0
    invalid = 0
    pages_read = 0
    seen_entry_ids: set[str] = set()
    stop = False
    for page in range(1, max_pages + 1):
        rows = client.entries(page=page, page_size=page_size)
        pages_read += 1
        if not rows:
            break
        for entry in rows:
            try:
                submitted_at = parse_datetime(
                    entry.get("date_created"),
                    "date_created",
                )
            except ValueError:
                invalid += 1
                continue
            if submitted_at < floor:
                stop = True
                continue
            observed += 1
            entry_id = str(entry.get("id") or "")
            if entry_id in seen_entry_ids:
                continue
            seen_entry_ids.add(entry_id)
            try:
                record = build_identity_record(
                    _entry_payload(entry),
                    secret=identity_secret,
                    school_bindings=school_bindings,
                    received_at=now,
                )
                store.upsert_identity(record)
                upserted += 1
            except (KeyError, TypeError, ValueError):
                invalid += 1
        if stop or len(rows) < page_size:
            break
    return CaptureRunResult(
        activation_start=activation.isoformat().replace("+00:00", "Z"),
        capture_floor=floor.isoformat().replace("+00:00", "Z"),
        entries_observed=observed,
        identities_upserted=upserted,
        invalid_entries=invalid,
        pages_read=pages_read,
    )
