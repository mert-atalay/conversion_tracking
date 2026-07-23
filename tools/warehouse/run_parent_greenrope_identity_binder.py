#!/usr/bin/env python3
"""Run the CEFA parent Form 4 to GreenRope identity binder."""

from __future__ import annotations

import json
import os

from parent_activation.greenrope_adapter import DEFAULT_ENDPOINT, GreenRopeClient
from parent_activation.identity_binder import run_identity_binder
from parent_activation.identity_store import ParentIdentityBigQueryStore


def _required_env(name: str) -> str:
    value = str(os.environ.get(name) or "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def _required_one(*names: str) -> str:
    for name in names:
        value = str(os.environ.get(name) or "").strip()
        if value:
            return value
    raise RuntimeError(f"{' or '.join(names)} is required")


def main() -> None:
    hmac_secret = _required_env("PARENT_ACTIVATION_HMAC_SECRET").encode("utf-8")
    result = run_identity_binder(
        store=ParentIdentityBigQueryStore(
            project_id=os.environ.get("GOOGLE_CLOUD_PROJECT")
            or "marketing-api-488017"
        ),
        client=GreenRopeClient(
            endpoint=os.environ.get("GREENROPE_API_URL") or DEFAULT_ENDPOINT,
            email=_required_one("GREENROPE_EMAIL", "GREENROPE_API_EMAIL"),
            token=_required_one("GREENROPE_TOKEN", "GREENROPE_API_TOKEN"),
            account_id=_required_env("GREENROPE_ACCOUNT_ID"),
        ),
        hmac_secret=hmac_secret,
        write_enabled=(
            str(os.environ.get("PARENT_GREENROPE_IDENTITY_WRITE_ENABLED") or "")
            .strip()
            .lower()
            == "true"
        ),
        limit=int(os.environ.get("PARENT_IDENTITY_BINDER_LIMIT") or "500"),
    )
    print(json.dumps(result.to_dict(), sort_keys=True))


if __name__ == "__main__":
    main()
