#!/usr/bin/env python3
"""Run the isolated CEFA parent Form 4 identity bridge."""

from __future__ import annotations

import os
from pathlib import Path

from parent_activation.identity_http import run_server
from parent_activation.identity_store import ParentIdentityBigQueryStore


def _required_env(name: str) -> str:
    value = str(os.environ.get(name) or "").strip()
    if not value:
        raise RuntimeError(f"{name} is required")
    return value


def main() -> None:
    run_server(
        host="0.0.0.0",
        port=int(os.environ.get("PORT") or "8080"),
        webhook_secret=_required_env("PARENT_IDENTITY_WEBHOOK_SECRET"),
        identity_secret=_required_env("PARENT_ACTIVATION_HMAC_SECRET").encode("utf-8"),
        school_map_path=Path(
            os.environ.get("PARENT_SCHOOL_MAP_PATH")
            or "/app/data/reference/cefa-parent-greenrope-school-map-v1.csv"
        ),
        store=ParentIdentityBigQueryStore(
            project_id=os.environ.get("GOOGLE_CLOUD_PROJECT")
            or "marketing-api-488017"
        ),
    )


if __name__ == "__main__":
    main()
