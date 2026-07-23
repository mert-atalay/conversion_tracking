#!/usr/bin/env python3
"""Dispatch eligible CEFA parent CRM outcomes in the configured mode."""

from __future__ import annotations

import argparse
import json
import os

from google.cloud import bigquery

from parent_activation.bigquery_store import ParentActivationBigQueryStore
from parent_activation.dispatcher import dispatch_due
from parent_activation.repository import ParentActivationRepository


def main() -> None:
    parser = argparse.ArgumentParser(description="Dispatch parent CRM platform events")
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "marketing-api-488017")
    bq_client = bigquery.Client(project=project_id)
    result = dispatch_due(
        repository=ParentActivationRepository(bq_client, project_id=project_id),
        store=ParentActivationBigQueryStore(bq_client, project_id=project_id),
        limit=args.limit,
    )
    print(json.dumps(result.to_dict(), sort_keys=True))


if __name__ == "__main__":
    main()
