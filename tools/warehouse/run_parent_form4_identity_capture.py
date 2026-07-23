#!/usr/bin/env python3
"""Capture prospective Form 4 identity into the restricted activation inbox."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from parent_activation.form4_capture import (
    WordPressGravityFormsClient,
    capture_new_form4_identities,
)
from parent_activation.identity_bridge import load_school_bindings, parse_datetime
from parent_activation.identity_store import ParentIdentityBigQueryStore


def _required_env(name: str) -> str:
    value = str(os.environ.get(name) or "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def main() -> None:
    store = ParentIdentityBigQueryStore(
        project_id=os.environ.get("GOOGLE_CLOUD_PROJECT")
        or "marketing-api-488017"
    )
    result = capture_new_form4_identities(
        client=WordPressGravityFormsClient(
            site_url=os.environ.get("PARENT_WORDPRESS_SITE_URL")
            or "https://cefa.ca",
            username=_required_env("PARENT_WORDPRESS_API_USERNAME"),
            application_password=_required_env(
                "PARENT_WORDPRESS_API_APPLICATION_PASSWORD"
            ),
        ),
        store=store,
        identity_secret=_required_env("PARENT_ACTIVATION_HMAC_SECRET").encode(
            "utf-8"
        ),
        school_bindings=load_school_bindings(
            Path(
                os.environ.get("PARENT_SCHOOL_MAP_PATH")
                or "/app/data/reference/cefa-parent-greenrope-school-map-v1.csv"
            )
        ),
        activation_start=parse_datetime(
            _required_env("PARENT_FORM4_CAPTURE_START_AT"),
            "PARENT_FORM4_CAPTURE_START_AT",
        ),
        observed_at=datetime.now(timezone.utc),
    )
    print(json.dumps(result.to_dict(), sort_keys=True))


if __name__ == "__main__":
    main()
