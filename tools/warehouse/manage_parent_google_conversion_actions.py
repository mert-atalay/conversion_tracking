#!/usr/bin/env python3
"""Safely manage CEFA parent CRM offline conversion actions in Google Ads."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable


CUSTOMER_ID = "4159217891"
DEFAULT_API_VERSION = "v22"
DEFAULT_CONFIG_FILE = Path.home() / ".config" / "google-ads.yaml"
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
BARE_ACTION_ID = re.compile(r"^[0-9]+$")


class SetupError(RuntimeError):
    """Raised when platform state cannot be reconciled safely."""


@dataclass(frozen=True)
class PlannedAction:
    name: str
    category: str


PLANNED_ACTIONS = (
    PlannedAction(
        "CEFA | Parent | CRM Tour Scheduled | GOOGLE",
        "BOOK_APPOINTMENT",
    ),
    PlannedAction(
        "CEFA | Parent | CRM Tour Completed Candidate | GOOGLE",
        "QUALIFIED_LEAD",
    ),
    PlannedAction(
        "CEFA | Parent | CRM Closed Won | GOOGLE",
        "CONVERTED_LEAD",
    ),
)


def conversion_action_create(spec: PlannedAction) -> dict[str, Any]:
    """Return the exact secondary UPLOAD_CLICKS action definition."""
    return {
        "name": spec.name,
        "category": spec.category,
        "type": "UPLOAD_CLICKS",
        "status": "ENABLED",
        "primaryForGoal": False,
        "countingType": "ONE_PER_CLICK",
        "clickThroughLookbackWindowDays": 90,
    }


def conversion_action_mutate_request(
    spec: PlannedAction,
    *,
    validate_only: bool,
) -> dict[str, Any]:
    return {
        "operations": [{"create": conversion_action_create(spec)}],
        "partialFailure": False,
        "validateOnly": validate_only,
        "responseContentType": "MUTABLE_RESOURCE",
    }


def _resource_id(resource_name: str) -> str:
    value = resource_name.rstrip("/").rsplit("/", 1)[-1]
    if not BARE_ACTION_ID.fullmatch(value):
        raise SetupError(
            f"Google returned an invalid conversion action resource: {resource_name}"
        )
    return value


def _field(row: dict[str, Any], resource: str) -> dict[str, Any]:
    value = row.get(resource)
    return value if isinstance(value, dict) else {}


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


@dataclass
class GoogleInventory:
    actions: list[dict[str, Any]]
    customer_goals: list[dict[str, Any]]
    campaign_goals: list[dict[str, Any]]
    custom_goals: list[dict[str, Any]]
    campaign_configs: list[dict[str, Any]]

    @classmethod
    def from_search_rows(
        cls,
        *,
        actions: Iterable[dict[str, Any]],
        customer_goals: Iterable[dict[str, Any]],
        campaign_goals: Iterable[dict[str, Any]],
        custom_goals: Iterable[dict[str, Any]],
        campaign_configs: Iterable[dict[str, Any]],
    ) -> "GoogleInventory":
        return cls(
            list(actions),
            list(customer_goals),
            list(campaign_goals),
            list(custom_goals),
            list(campaign_configs),
        )

    def actions_named(self, name: str) -> list[dict[str, Any]]:
        return [
            _field(row, "conversionAction")
            for row in self.actions
            if str(_field(row, "conversionAction").get("name") or "") == name
        ]

    def customer_goal(self, category: str, origin: str) -> dict[str, Any] | None:
        for row in self.customer_goals:
            goal = _field(row, "customerConversionGoal")
            if goal.get("category") == category and goal.get("origin") == origin:
                return goal
        return None

    def active_actions_for_goal(
        self,
        category: str,
        origin: str,
    ) -> list[dict[str, Any]]:
        return [
            _field(row, "conversionAction")
            for row in self.actions
            if (
                _field(row, "conversionAction").get("category") == category
                and _field(row, "conversionAction").get("origin") == origin
                and _field(row, "conversionAction").get("status") != "REMOVED"
            )
        ]

    def biddable_campaign_goals(
        self,
        category: str,
        origin: str,
    ) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for row in self.campaign_goals:
            goal = _field(row, "campaignConversionGoal")
            if (
                goal.get("category") == category
                and goal.get("origin") == origin
                and _bool(goal.get("biddable"))
            ):
                matches.append(row)
        return matches

    def custom_goals_containing(self, resource_name: str) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for row in self.custom_goals:
            goal = _field(row, "customConversionGoal")
            actions = [str(value) for value in goal.get("conversionActions") or []]
            if resource_name in actions and goal.get("status") != "REMOVED":
                matches.append(goal)
        return matches

    def summary(self) -> dict[str, int]:
        return {
            "conversion_actions": len(self.actions),
            "customer_goals": len(self.customer_goals),
            "campaign_goals": len(self.campaign_goals),
            "custom_goals": len(self.custom_goals),
            "campaign_goal_configs": len(self.campaign_configs),
        }


def _verify_existing_action(
    spec: PlannedAction,
    action: dict[str, Any],
    inventory: GoogleInventory,
    *,
    require_goal_safe: bool = False,
) -> dict[str, Any]:
    resource_name = str(action.get("resourceName") or "")
    action_id = str(action.get("id") or "")
    if not action_id and resource_name:
        action_id = _resource_id(resource_name)
    if not BARE_ACTION_ID.fullmatch(action_id):
        raise SetupError(f"{spec.name} does not have a bare numeric action ID.")

    expected = {
        "type": "UPLOAD_CLICKS",
        "category": spec.category,
        "countingType": "ONE_PER_CLICK",
        "primaryForGoal": False,
        "status": "ENABLED",
    }
    mismatches = {
        key: {"expected": value, "actual": action.get(key)}
        for key, value in expected.items()
        if (
            _bool(action.get(key)) != value
            if isinstance(value, bool)
            else action.get(key) != value
        )
    }
    if mismatches:
        raise SetupError(
            f"Existing action conflicts with the required definition: "
            f"{spec.name}: {json.dumps(mismatches, sort_keys=True)}"
        )

    custom_goals = inventory.custom_goals_containing(resource_name)
    if custom_goals:
        names = sorted(str(goal.get("name") or goal.get("id") or "") for goal in custom_goals)
        raise SetupError(
            f"{spec.name} is included in a custom conversion goal and could be "
            f"biddable despite secondary status: {', '.join(names)}"
        )

    origin = str(action.get("origin") or "")
    if not origin:
        raise SetupError(f"{spec.name} does not have a conversion origin.")
    active_pair_actions = inventory.active_actions_for_goal(spec.category, origin)
    if len(active_pair_actions) != 1 or str(
        active_pair_actions[0].get("resourceName") or ""
    ) != resource_name:
        names = sorted(
            str(item.get("name") or item.get("id") or "")
            for item in active_pair_actions
        )
        raise SetupError(
            f"{spec.name} shares its {spec.category}/{origin} goal pair with "
            f"another active conversion action: {', '.join(names)}"
        )

    customer_goal = inventory.customer_goal(spec.category, origin)
    if not customer_goal:
        raise SetupError(
            f"{spec.name} is missing its generated customer conversion goal."
        )
    campaign_goal_count = len(
        inventory.biddable_campaign_goals(spec.category, origin)
    )
    customer_goal_biddable = _bool(customer_goal.get("biddable"))
    if require_goal_safe and (customer_goal_biddable or campaign_goal_count):
        raise SetupError(
            f"{spec.name} remains biddable through its generated account or "
            f"campaign conversion goal."
        )
    return {
        "name": spec.name,
        "action_id": action_id,
        "resource_name": resource_name,
        "category": spec.category,
        "origin": origin,
        "status": "existing_match",
        "secondary": True,
        "customer_goal_resource_name": customer_goal.get("resourceName"),
        "customer_goal_biddable": customer_goal_biddable,
        "biddable_campaign_goal_count": campaign_goal_count,
        "custom_goal_inclusions": 0,
        "goal_safety": (
            "the action is secondary and its exclusive category/origin goal is "
            "excluded from account-default and campaign bidding"
            if not customer_goal_biddable and not campaign_goal_count
            else "the exclusive generated category/origin goal must be disabled"
        ),
    }


def _planned_result(spec: PlannedAction, status: str) -> dict[str, Any]:
    return {
        "name": spec.name,
        "action_id": "",
        "resource_name": "",
        "status": status,
        "secondary": True,
        "customer_goal_biddable": None,
        "biddable_campaign_goal_count": 0,
        "custom_goal_inclusions": 0,
        "goal_safety": "no customer, campaign, or custom goal mutations are planned",
    }


def reconcile_google_actions(
    client: Any,
    *,
    mode: str,
) -> dict[str, Any]:
    """Inventory first, then validate/create/read back the approved actions."""
    if mode not in {"validate_only", "apply", "read_back"}:
        raise ValueError(f"Unsupported mode: {mode}")

    before: GoogleInventory = client.inventory()
    results: list[dict[str, Any]] = []
    created_names: set[str] = set()

    for spec in PLANNED_ACTIONS:
        matches = before.actions_named(spec.name)
        if len(matches) > 1:
            raise SetupError(f"Duplicate Google conversion action name: {spec.name}")
        if matches:
            results.append(_verify_existing_action(spec, matches[0], before))
            continue
        if mode == "read_back":
            results.append(_planned_result(spec, "missing"))
            continue

        client.mutate_conversion_action(spec, validate_only=True)
        if mode == "validate_only":
            results.append(_planned_result(spec, "validated"))
            continue

        response = client.mutate_conversion_action(spec, validate_only=False)
        resource_name = str(response.get("resourceName") or "")
        results.append(
            {
                **_planned_result(spec, "created_pending_read_back"),
                "action_id": _resource_id(resource_name),
                "resource_name": resource_name,
            }
        )
        created_names.add(spec.name)

    if mode == "validate_only":
        return {
            "mode": mode,
            "customer_id": client.customer_id,
            "inventory": before.summary(),
            "actions": results,
            "goal_mutations": 0,
        }

    after: GoogleInventory = before if mode == "read_back" else client.inventory()
    goal_mutations = 0
    if mode == "apply":
        for spec in PLANNED_ACTIONS:
            matches = after.actions_named(spec.name)
            if len(matches) != 1:
                continue
            item = _verify_existing_action(spec, matches[0], after)
            if not item["customer_goal_biddable"]:
                continue
            goal_resource_name = str(item["customer_goal_resource_name"])
            client.mutate_customer_conversion_goal(
                goal_resource_name,
                biddable=False,
                validate_only=True,
            )
            client.mutate_customer_conversion_goal(
                goal_resource_name,
                biddable=False,
                validate_only=False,
            )
            goal_mutations += 1
        if goal_mutations:
            after = client.inventory()

    verified: list[dict[str, Any]] = []
    missing: list[str] = []
    for spec in PLANNED_ACTIONS:
        matches = after.actions_named(spec.name)
        if not matches:
            missing.append(spec.name)
            continue
        if len(matches) > 1:
            raise SetupError(f"Duplicate Google conversion action name: {spec.name}")
        item = _verify_existing_action(
            spec,
            matches[0],
            after,
            require_goal_safe=True,
        )
        if spec.name in created_names:
            item["status"] = "created_and_verified"
        verified.append(item)
    if missing:
        raise SetupError(
            "Read-back is missing required Google conversion actions: "
            + ", ".join(missing)
        )

    return {
        "mode": mode,
        "customer_id": client.customer_id,
        "inventory": after.summary(),
        "actions": verified,
        "goal_mutations": goal_mutations,
    }


def _read_config(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if path.exists():
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")

    env_names = {
        "developer_token": "GOOGLE_ADS_DEVELOPER_TOKEN",
        "client_id": "GOOGLE_ADS_CLIENT_ID",
        "client_secret": "GOOGLE_ADS_CLIENT_SECRET",
        "refresh_token": "GOOGLE_ADS_REFRESH_TOKEN",
        "login_customer_id": "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
    }
    for key, env_name in env_names.items():
        value = os.getenv(env_name, "").strip()
        if value:
            values[key] = value
    missing = [
        key
        for key in ("developer_token", "client_id", "client_secret", "refresh_token")
        if not values.get(key)
    ]
    if missing:
        raise SetupError(
            f"Missing Google Ads API credentials: {', '.join(sorted(missing))}"
        )
    return values


def _request_json(
    request: urllib.request.Request,
    *,
    retries: int = 4,
) -> Any:
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code in RETRYABLE_STATUS_CODES and attempt < retries:
                time.sleep(2**attempt)
                continue
            raise SetupError(f"Google Ads API HTTP {exc.code}: {body[:2000]}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt < retries:
                time.sleep(2**attempt)
                continue
            raise SetupError(f"Google Ads API request failed: {exc}") from exc
    raise SetupError("Google Ads API request exhausted retries.")


def _access_token(config: dict[str, str]) -> str:
    body = urllib.parse.urlencode(
        {
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "refresh_token": config["refresh_token"],
            "grant_type": "refresh_token",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=body,
        method="POST",
    )
    payload = _request_json(request)
    token = str(payload.get("access_token") or "")
    if not token:
        raise SetupError("Google OAuth refresh returned no access token.")
    return token


class GoogleAdsClient:
    def __init__(
        self,
        *,
        customer_id: str,
        api_version: str,
        config: dict[str, str],
        request_json: Callable[..., Any] = _request_json,
    ) -> None:
        self.customer_id = customer_id.replace("-", "")
        self.api_version = api_version
        self.config = config
        self.request_json = request_json
        self.token = _access_token(config)

    def _headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "developer-token": self.config["developer_token"],
            "Content-Type": "application/json",
        }
        login_customer_id = self.config.get("login_customer_id", "").replace("-", "")
        if login_customer_id:
            headers["login-customer-id"] = login_customer_id
        return headers

    def _post(self, service: str, payload: dict[str, Any]) -> Any:
        request = urllib.request.Request(
            (
                f"https://googleads.googleapis.com/{self.api_version}/customers/"
                f"{self.customer_id}/{service}"
            ),
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        return self.request_json(request)

    def search(self, query: str) -> list[dict[str, Any]]:
        chunks = self._post("googleAds:searchStream", {"query": query})
        if not isinstance(chunks, list):
            raise SetupError("Unexpected Google Ads searchStream response shape.")
        return [
            row
            for chunk in chunks
            for row in (chunk.get("results") or [])
            if isinstance(row, dict)
        ]

    def inventory(self) -> GoogleInventory:
        return GoogleInventory.from_search_rows(
            actions=self.search(
                """
                SELECT
                  conversion_action.resource_name,
                  conversion_action.id,
                  conversion_action.name,
                  conversion_action.status,
                  conversion_action.type,
                  conversion_action.category,
                  conversion_action.origin,
                  conversion_action.primary_for_goal,
                  conversion_action.counting_type,
                  conversion_action.click_through_lookback_window_days,
                  conversion_action.value_settings.default_value,
                  conversion_action.value_settings.always_use_default_value
                FROM conversion_action
                """
            ),
            customer_goals=self.search(
                """
                SELECT
                  customer_conversion_goal.resource_name,
                  customer_conversion_goal.category,
                  customer_conversion_goal.origin,
                  customer_conversion_goal.biddable
                FROM customer_conversion_goal
                """
            ),
            campaign_goals=self.search(
                """
                SELECT
                  campaign.id,
                  campaign.name,
                  campaign.status,
                  campaign_conversion_goal.resource_name,
                  campaign_conversion_goal.category,
                  campaign_conversion_goal.origin,
                  campaign_conversion_goal.biddable
                FROM campaign_conversion_goal
                """
            ),
            custom_goals=self.search(
                """
                SELECT
                  custom_conversion_goal.resource_name,
                  custom_conversion_goal.id,
                  custom_conversion_goal.name,
                  custom_conversion_goal.status,
                  custom_conversion_goal.conversion_actions
                FROM custom_conversion_goal
                """
            ),
            campaign_configs=self.search(
                """
                SELECT
                  campaign.id,
                  campaign.name,
                  conversion_goal_campaign_config.goal_config_level,
                  conversion_goal_campaign_config.custom_conversion_goal
                FROM conversion_goal_campaign_config
                """
            ),
        )

    def mutate_conversion_action(
        self,
        spec: PlannedAction,
        *,
        validate_only: bool,
    ) -> dict[str, Any]:
        payload = self._post(
            "conversionActions:mutate",
            conversion_action_mutate_request(spec, validate_only=validate_only),
        )
        if validate_only:
            return {"validated": True}
        results = payload.get("results") or []
        if len(results) != 1:
            raise SetupError(
                f"Google Ads did not return one mutation result for {spec.name}."
            )
        result = results[0]
        resource_name = str(
            result.get("resourceName")
            or _field(result, "conversionAction").get("resourceName")
            or ""
        )
        _resource_id(resource_name)
        return {"resourceName": resource_name}

    def mutate_customer_conversion_goal(
        self,
        resource_name: str,
        *,
        biddable: bool,
        validate_only: bool,
    ) -> dict[str, Any]:
        if not resource_name.startswith(
            f"customers/{self.customer_id}/customerConversionGoals/"
        ):
            raise SetupError(
                f"Unexpected customer conversion goal resource: {resource_name}"
            )
        payload = self._post(
            "customerConversionGoals:mutate",
            {
                "operations": [
                    {
                        "update": {
                            "resourceName": resource_name,
                            "biddable": biddable,
                        },
                        "updateMask": "biddable",
                    }
                ],
                "validateOnly": validate_only,
            },
        )
        if validate_only:
            return {"validated": True}
        results = payload.get("results") or []
        if len(results) != 1:
            raise SetupError(
                "Google Ads did not return one customer conversion goal result."
            )
        return {"resourceName": str(results[0].get("resourceName") or resource_name)}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory and safely create secondary CEFA parent CRM Google Ads "
            "UPLOAD_CLICKS conversion actions."
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate-only", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--read-back", action="store_true")
    parser.add_argument("--customer-id", default=CUSTOMER_ID)
    parser.add_argument(
        "--api-version",
        default=os.getenv("GOOGLE_ADS_API_VERSION", DEFAULT_API_VERSION),
    )
    parser.add_argument("--config-file", type=Path, default=DEFAULT_CONFIG_FILE)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.apply and os.getenv("CEFA_GOOGLE_ADS_ENABLE_WRITES", "").strip() != "1":
        raise SetupError(
            "Set CEFA_GOOGLE_ADS_ENABLE_WRITES=1 to permit Google Ads writes."
        )
    config = _read_config(args.config_file)
    client = GoogleAdsClient(
        customer_id=args.customer_id,
        api_version=args.api_version,
        config=config,
    )
    selected_mode = (
        "apply"
        if args.apply
        else "read_back"
        if args.read_back
        else "validate_only"
    )
    report = reconcile_google_actions(client, mode=selected_mode)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SetupError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
