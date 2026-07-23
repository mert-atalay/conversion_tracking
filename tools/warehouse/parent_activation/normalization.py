"""Transient normalization, hashing, HMAC, and platform age helpers."""

from __future__ import annotations

import hashlib
import hmac
import re
from datetime import datetime, timedelta, timezone
from typing import Final


_SPACE_RE: Final = re.compile(r"\s+")
_PHONE_RE: Final = re.compile(r"\D+")
_STAGE_SEPARATORS_RE: Final = re.compile(r"[^a-z0-9]+")


def normalize_text(value: object | None) -> str:
    return _SPACE_RE.sub(" ", str(value or "").strip())


def normalize_stage_label(value: object | None) -> str:
    text = normalize_text(value).lower()
    return _STAGE_SEPARATORS_RE.sub(" ", text).strip()


def normalize_email(value: object | None) -> str:
    """Return the common enhanced-conversion email representation."""
    return re.sub(r"\s+", "", normalize_text(value).lower())


def normalize_phone(value: object | None, default_country_calling_code: str = "1") -> str:
    """Return an E.164-like phone number without retaining the original input.

    Parent inquiries are Canada/US scoped by default, so a ten-digit number is
    normalized to ``+1``. Callers with a known international number should pass
    it with a leading ``+`` or a country calling code.
    """
    raw = normalize_text(value)
    digits = _PHONE_RE.sub("", raw)
    if digits.startswith("00"):
        digits = digits[2:]
    elif raw.startswith("+"):
        pass
    elif len(digits) == 10:
        digits = f"{default_country_calling_code}{digits}"
    elif len(digits) == 11 and digits.startswith("1"):
        pass
    if not 7 <= len(digits) <= 15:
        return ""
    return f"+{digits}"


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_normalized_email(value: object | None) -> str | None:
    normalized = normalize_email(value)
    return sha256_hex(normalized) if normalized else None


def sha256_normalized_phone(value: object | None, default_country_calling_code: str = "1") -> str | None:
    normalized = normalize_phone(value, default_country_calling_code)
    return sha256_hex(normalized) if normalized else None


def hmac_platform_event_id(
    secret: bytes | str,
    source_account: str,
    identity_scope: str,
    subject_id: str,
    stage: str,
    subject_occurrence: int = 1,
) -> str:
    """Return a stable platform-safe ID from a caller-supplied Secret Manager value."""
    if not secret:
        raise ValueError("An HMAC secret is required")
    if subject_occurrence < 1:
        raise ValueError("subject_occurrence must be at least 1")
    key = secret.encode("utf-8") if isinstance(secret, str) else secret
    fields = (source_account, identity_scope, subject_id, stage, str(subject_occurrence))
    if any(not value for value in fields):
        raise ValueError("HMAC identity fields must be non-empty")
    payload = "|".join(fields).encode("utf-8")
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def _is_within_age(event_at: datetime, reference_at: datetime, maximum_age: timedelta) -> bool:
    if event_at.tzinfo is None or reference_at.tzinfo is None:
        raise ValueError("event_at and reference_at must be timezone-aware")
    age = reference_at.astimezone(timezone.utc) - event_at.astimezone(timezone.utc)
    return timedelta(0) <= age <= maximum_age


def google_click_id_is_eligible(click_at: datetime, conversion_at: datetime) -> bool:
    from .config import GOOGLE_CLICK_ID_MAX_AGE

    return _is_within_age(click_at, conversion_at, GOOGLE_CLICK_ID_MAX_AGE)


def google_user_data_is_eligible(captured_at: datetime, conversion_at: datetime) -> bool:
    from .config import GOOGLE_USER_DATA_MAX_AGE

    return _is_within_age(captured_at, conversion_at, GOOGLE_USER_DATA_MAX_AGE)


def meta_event_is_eligible(event_at: datetime, sent_at: datetime) -> bool:
    from .config import META_EVENT_MAX_AGE

    return _is_within_age(event_at, sent_at, META_EVENT_MAX_AGE)
