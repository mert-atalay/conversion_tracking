#!/usr/bin/env python3
"""Retrieve Google Data Manager diagnostics for processing parent events."""

from __future__ import annotations

import argparse
import json
import os

from google.cloud import bigquery

from parent_activation.bigquery_store import ParentActivationBigQueryStore
from parent_activation.dispatcher import refresh_google_diagnostics
from parent_activation.repository import ParentActivationRepository


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh parent Google delivery diagnostics")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "marketing-api-488017")
    bq_client = bigquery.Client(project=project_id)
    result = refresh_google_diagnostics(
        repository=ParentActivationRepository(bq_client, project_id=project_id),
        store=ParentActivationBigQueryStore(bq_client, project_id=project_id),
        limit=args.limit,
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
