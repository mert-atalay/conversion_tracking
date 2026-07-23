#!/usr/bin/env python3
"""Read-only GreenRope opportunity-field dictionary snapshot."""

from __future__ import annotations

import json
import os
from dataclasses import asdict

from parent_activation.greenrope_adapter import DEFAULT_ENDPOINT, GreenRopeClient, evaluate_required_fields


def main() -> None:
    email = os.environ.get("GREENROPE_EMAIL") or os.environ.get("GR_EMAIL")
    token = os.environ.get("GREENROPE_TOKEN") or os.environ.get("GR_TOKEN") or os.environ.get("GREENROPE_AUTH_TOKEN")
    account_id = os.environ.get("GREENROPE_ACCOUNT_ID") or os.environ.get("GR_ACCOUNT")
    if not all((email, token, account_id)):
        raise SystemExit("Missing GREENROPE_EMAIL, GREENROPE_TOKEN, or GREENROPE_ACCOUNT_ID")
    client = GreenRopeClient(os.environ.get("GREENROPE_API_URL", DEFAULT_ENDPOINT), email, token, account_id)
    fields = client.opportunity_fields()
    readiness = evaluate_required_fields(field.normalized_label for field in fields)
    print(json.dumps({"readiness": readiness.to_safe_dict(), "fields": [asdict(field) for field in fields]}))


if __name__ == "__main__":
    main()
