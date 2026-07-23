#!/usr/bin/env python3
"""Manage reporting-only Meta custom conversions for parent CRM outcomes."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable


META_AD_ACCOUNT_ID = "1595846967472729"
META_DATASET_ID = "918227085392601"
DEFAULT_API_VERSION = "v25.0"
CUSTOM_EVENT_TYPE = "LEAD"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class SetupError(RuntimeError):
    """Raised when Meta state cannot be reconciled safely."""


@dataclass(frozen=True)
class PlannedCustomConversion:
    name: str
    event_name: str


PLANNED_CONVERSIONS = (
    PlannedCustomConversion(
        "CEFA | Parent | CRM Tour Scheduled | META",
        "CEFA_CRM_TourScheduled",
    ),
    PlannedCustomConversion(
        "CEFA | Parent | CRM Tour Completed Candidate | META",
        "CEFA_CRM_TourCompletedCandidate",
    ),
    PlannedCustomConversion(
        "CEFA | Parent | CRM Closed Won | META",
        "CEFA_CRM_ClosedWon",
    ),
)


def normalize_account_id(value: str) -> str:
    clean = value.strip()
    return clean if clean.startswith("act_") else f"act_{clean}"


def conversion_rule(event_name: str) -> dict[str, Any]:
    return {"and": [{"event": {"eq": event_name}}]}


def canonical_rule(value: Any) -> str:
    if isinstance(value, str):
        value = json.loads(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def custom_conversion_create(
    spec: PlannedCustomConversion,
    *,
    dataset_id: str = META_DATASET_ID,
) -> dict[str, Any]:
    return {
        "name": spec.name,
        "event_source_id": dataset_id,
        "custom_event_type": CUSTOM_EVENT_TYPE,
        "rule": conversion_rule(spec.event_name),
    }


def _event_source_id(row: dict[str, Any]) -> str:
    pixel = row.get("pixel")
    if isinstance(pixel, dict) and pixel.get("id"):
        return str(pixel["id"])
    return str(row.get("event_source_id") or row.get("eventSourceId") or "")


def _verify_existing(
    spec: PlannedCustomConversion,
    row: dict[str, Any],
    *,
    dataset_id: str,
) -> dict[str, Any]:
    expected_rule = canonical_rule(conversion_rule(spec.event_name))
    actual_rule = canonical_rule(row.get("rule") or {})
    mismatches: dict[str, dict[str, Any]] = {}
    expected = {
        "event_source_id": dataset_id,
        "custom_event_type": CUSTOM_EVENT_TYPE,
        "rule": expected_rule,
        "is_archived": False,
        "is_unavailable": False,
    }
    actual = {
        "event_source_id": _event_source_id(row),
        "custom_event_type": str(row.get("custom_event_type") or ""),
        "rule": actual_rule,
        "is_archived": bool(row.get("is_archived", False)),
        "is_unavailable": bool(row.get("is_unavailable", False)),
    }
    for key, value in expected.items():
        if actual[key] != value:
            mismatches[key] = {"expected": value, "actual": actual[key]}
    if mismatches:
        raise SetupError(
            f"Existing Meta custom conversion conflicts with the required "
            f"reporting definition: {spec.name}: "
            f"{json.dumps(mismatches, sort_keys=True)}"
        )
    conversion_id = str(row.get("id") or "")
    if not conversion_id:
        raise SetupError(f"Meta custom conversion has no ID: {spec.name}")
    return {
        "name": spec.name,
        "event_name": spec.event_name,
        "custom_conversion_id": conversion_id,
        "status": "existing_match",
        "event_source_id": dataset_id,
        "reporting_only": True,
        "optimization_mutations": 0,
        "rule": expected_rule,
    }


def _semantic_duplicates(
    spec: PlannedCustomConversion,
    existing: list[dict[str, Any]],
    *,
    dataset_id: str,
) -> list[str]:
    expected_rule = canonical_rule(conversion_rule(spec.event_name))
    return sorted(
        str(row.get("name") or row.get("id") or "")
        for row in existing
        if str(row.get("name") or "") != spec.name
        and _event_source_id(row) == dataset_id
        and canonical_rule(row.get("rule") or {}) == expected_rule
        and not bool(row.get("is_archived", False))
    )


def reconcile_meta_conversions(
    client: Any,
    *,
    mode: str,
    dataset_id: str = META_DATASET_ID,
) -> dict[str, Any]:
    """Inventory first, then plan/create/read back reporting-only conversions."""
    if mode not in {"dry_run", "apply", "read_back"}:
        raise ValueError(f"Unsupported mode: {mode}")

    before: list[dict[str, Any]] = client.inventory()
    results: list[dict[str, Any]] = []
    created_names: set[str] = set()

    for spec in PLANNED_CONVERSIONS:
        matches = [
            row for row in before if str(row.get("name") or "") == spec.name
        ]
        if len(matches) > 1:
            raise SetupError(f"Duplicate Meta custom conversion name: {spec.name}")
        if matches:
            results.append(_verify_existing(spec, matches[0], dataset_id=dataset_id))
            continue
        duplicates = _semantic_duplicates(spec, before, dataset_id=dataset_id)
        if duplicates:
            raise SetupError(
                f"Meta already has a differently named custom conversion for "
                f"{spec.event_name}: {', '.join(duplicates)}"
            )
        if mode == "read_back":
            results.append(
                {
                    "name": spec.name,
                    "event_name": spec.event_name,
                    "custom_conversion_id": "",
                    "status": "missing",
                    "event_source_id": dataset_id,
                    "reporting_only": True,
                    "optimization_mutations": 0,
                    "rule": canonical_rule(conversion_rule(spec.event_name)),
                }
            )
            continue
        if mode == "dry_run":
            results.append(
                {
                    "name": spec.name,
                    "event_name": spec.event_name,
                    "custom_conversion_id": "",
                    "status": "planned",
                    "event_source_id": dataset_id,
                    "reporting_only": True,
                    "optimization_mutations": 0,
                    "rule": canonical_rule(conversion_rule(spec.event_name)),
                }
            )
            continue

        response = client.create(spec, dataset_id=dataset_id)
        conversion_id = str(response.get("id") or "")
        if not conversion_id:
            raise SetupError(f"Meta did not return an ID for {spec.name}.")
        results.append(
            {
                "name": spec.name,
                "event_name": spec.event_name,
                "custom_conversion_id": conversion_id,
                "status": "created_pending_read_back",
                "event_source_id": dataset_id,
                "reporting_only": True,
                "optimization_mutations": 0,
                "rule": canonical_rule(conversion_rule(spec.event_name)),
            }
        )
        created_names.add(spec.name)

    if mode == "dry_run":
        return {
            "mode": mode,
            "ad_account_id": client.account_id,
            "dataset_id": dataset_id,
            "existing_custom_conversions": len(before),
            "custom_conversions": results,
            "campaign_or_ad_set_mutations": 0,
        }

    after = before if mode == "read_back" else client.inventory()
    verified: list[dict[str, Any]] = []
    missing: list[str] = []
    for spec in PLANNED_CONVERSIONS:
        matches = [row for row in after if str(row.get("name") or "") == spec.name]
        if not matches:
            missing.append(spec.name)
            continue
        if len(matches) > 1:
            raise SetupError(f"Duplicate Meta custom conversion name: {spec.name}")
        item = _verify_existing(spec, matches[0], dataset_id=dataset_id)
        if spec.name in created_names:
            item["status"] = "created_and_verified"
        verified.append(item)
    if missing:
        raise SetupError(
            "Read-back is missing required Meta custom conversions: "
            + ", ".join(missing)
        )

    return {
        "mode": mode,
        "ad_account_id": client.account_id,
        "dataset_id": dataset_id,
        "existing_custom_conversions": len(after),
        "custom_conversions": verified,
        "campaign_or_ad_set_mutations": 0,
    }


class MetaClient:
    def __init__(
        self,
        *,
        account_id: str,
        access_token: str,
        api_version: str,
        request: Callable[..., Any] | None = None,
    ) -> None:
        self.account_id = normalize_account_id(account_id)
        self.access_token = access_token
        self.api_version = api_version
        self.request_override = request

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any],
        *,
        retries: int = 4,
    ) -> Any:
        if self.request_override is not None:
            return self.request_override(method, path, params)

        url = f"https://graph.facebook.com/{self.api_version}/{path.lstrip('/')}"
        data = dict(params)
        data["access_token"] = self.access_token
        encoded = urllib.parse.urlencode(
            {
                key: (
                    json.dumps(value, separators=(",", ":"))
                    if isinstance(value, (dict, list))
                    else str(value)
                )
                for key, value in data.items()
                if value is not None
            }
        )
        request = (
            urllib.request.Request(f"{url}?{encoded}", method="GET")
            if method == "GET"
            else urllib.request.Request(
                url,
                data=encoded.encode("utf-8"),
                method=method,
            )
        )
        for attempt in range(retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    body = response.read().decode("utf-8")
                    return json.loads(body) if body else {}
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                if exc.code in RETRYABLE_STATUS_CODES and attempt < retries:
                    time.sleep(2**attempt)
                    continue
                raise SetupError(f"Meta API HTTP {exc.code}: {body[:2000]}") from exc
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                if attempt < retries:
                    time.sleep(2**attempt)
                    continue
                raise SetupError(f"Meta API request failed: {exc}") from exc
        raise SetupError("Meta API request exhausted retries.")

    def get_all(self, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        payload = self.request("GET", path, params)
        rows = list(payload.get("data") or [])
        next_url = (payload.get("paging") or {}).get("next")
        while next_url:
            request = urllib.request.Request(next_url, method="GET")
            try:
                with urllib.request.urlopen(request, timeout=60) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except (urllib.error.HTTPError, urllib.error.URLError) as exc:
                raise SetupError(f"Meta pagination failed: {exc}") from exc
            rows.extend(payload.get("data") or [])
            next_url = (payload.get("paging") or {}).get("next")
        return rows

    def inventory(self) -> list[dict[str, Any]]:
        return self.get_all(
            f"{self.account_id}/customconversions",
            {
                "fields": (
                    "id,name,custom_event_type,pixel{id,name},event_source_type,"
                    "creation_time,is_archived,is_unavailable,rule"
                ),
                "limit": 100,
            },
        )

    def create(
        self,
        spec: PlannedCustomConversion,
        *,
        dataset_id: str,
    ) -> dict[str, Any]:
        return self.request(
            "POST",
            f"{self.account_id}/customconversions",
            custom_conversion_create(spec, dataset_id=dataset_id),
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory and idempotently create reporting-only Meta custom "
            "conversions for CEFA parent CRM lifecycle events."
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--read-back", action="store_true")
    parser.add_argument("--ad-account-id", default=META_AD_ACCOUNT_ID)
    parser.add_argument("--dataset-id", default=META_DATASET_ID)
    parser.add_argument(
        "--api-version",
        default=os.getenv("META_API_VERSION", DEFAULT_API_VERSION),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.apply and os.getenv("CEFA_META_ENABLE_WRITES", "").strip() != "1":
        raise SetupError("Set CEFA_META_ENABLE_WRITES=1 to permit Meta writes.")
    access_token = os.getenv("META_ACCESS_TOKEN", "").strip()
    if not access_token:
        raise SetupError("Required environment value is missing: META_ACCESS_TOKEN")
    client = MetaClient(
        account_id=args.ad_account_id,
        access_token=access_token,
        api_version=args.api_version,
    )
    selected_mode = (
        "apply" if args.apply else "read_back" if args.read_back else "dry_run"
    )
    report = reconcile_meta_conversions(
        client,
        mode=selected_mode,
        dataset_id=args.dataset_id,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SetupError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
