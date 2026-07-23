#!/usr/bin/env python3
"""Run the production BQ-backed parent GreenRope lifecycle poll."""

from __future__ import annotations

import argparse
import json
import os

from google.cloud import bigquery

from parent_activation.bigquery_store import ParentActivationBigQueryStore
from parent_activation.greenrope_adapter import DEFAULT_ENDPOINT, GreenRopeClient
from parent_activation.poller_runtime import run_poll
from parent_activation.repository import ParentActivationRepository


def _required(*names: str) -> str:
    for name in names:
        value = str(os.environ.get(name) or "").strip()
        if value:
            return value
    raise SystemExit(f"Missing required environment value: {' or '.join(names)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Poll GreenRope and persist prospective parent CRM lifecycle state"
    )
    parser.add_argument("--group-ids", help="Optional comma-separated controlled group list")
    parser.add_argument("--max-workers", type=int, default=4)
    args = parser.parse_args()
    configured_group_ids = (
        args.group_ids or os.environ.get("PARENT_GREENROPE_GROUP_IDS", "")
    )
    controlled_group_ids = {
        value.strip()
        for value in configured_group_ids.split(",")
        if value.strip()
    }
    if not controlled_group_ids:
        raise SystemExit(
            "Missing required parent GreenRope group allowlist: "
            "--group-ids or PARENT_GREENROPE_GROUP_IDS"
        )

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "marketing-api-488017")
    secret = _required("PARENT_ACTIVATION_HMAC_SECRET").encode("utf-8")
    greenrope = GreenRopeClient(
        os.environ.get("GREENROPE_API_URL", DEFAULT_ENDPOINT),
        _required("GREENROPE_EMAIL", "GR_EMAIL"),
        _required("GREENROPE_TOKEN", "GR_TOKEN", "GREENROPE_AUTH_TOKEN"),
        _required("GREENROPE_ACCOUNT_ID", "GR_ACCOUNT"),
        int(os.environ.get("GREENROPE_REQUEST_TIMEOUT_SECONDS", "120")),
    )
    bq_client = bigquery.Client(project=project_id)
    result = run_poll(
        client=greenrope,
        repository=ParentActivationRepository(bq_client, project_id=project_id),
        store=ParentActivationBigQueryStore(
            bq_client,
            project_id=project_id,
            transaction_secret=secret,
        ),
        secret=secret,
        group_ids=controlled_group_ids,
        max_workers=args.max_workers,
    )
    print(json.dumps(result.to_dict(), sort_keys=True))


if __name__ == "__main__":
    main()
