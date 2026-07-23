from __future__ import annotations

import unittest

import manage_parent_google_conversion_actions as google_setup
import manage_parent_meta_custom_conversions as meta_setup


def google_action_row(
    spec: google_setup.PlannedAction,
    action_id: str,
    *,
    primary: bool = False,
    action_type: str = "UPLOAD_CLICKS",
) -> dict[str, object]:
    return {
        "conversionAction": {
            "resourceName": (
                f"customers/{google_setup.CUSTOMER_ID}/conversionActions/{action_id}"
            ),
            "id": action_id,
            "name": spec.name,
            "status": "ENABLED",
            "type": action_type,
            "category": spec.category,
            "origin": "WEBSITE",
            "primaryForGoal": primary,
            "countingType": "ONE_PER_CLICK",
        }
    }


class FakeGoogleClient:
    customer_id = google_setup.CUSTOMER_ID

    def __init__(
        self,
        before: google_setup.GoogleInventory,
        after: google_setup.GoogleInventory | None = None,
        final: google_setup.GoogleInventory | None = None,
    ) -> None:
        middle = after or before
        self.inventories = [before, middle, final or middle]
        self.inventory_calls = 0
        self.mutations: list[tuple[str, bool]] = []
        self.goal_mutations: list[tuple[str, bool, bool]] = []

    def inventory(self) -> google_setup.GoogleInventory:
        index = min(self.inventory_calls, len(self.inventories) - 1)
        self.inventory_calls += 1
        return self.inventories[index]

    def mutate_conversion_action(
        self,
        spec: google_setup.PlannedAction,
        *,
        validate_only: bool,
    ) -> dict[str, str | bool]:
        self.mutations.append((spec.name, validate_only))
        action_id = str(9000 + len(self.mutations))
        return (
            {"validated": True}
            if validate_only
            else {
                "resourceName": (
                    f"customers/{self.customer_id}/conversionActions/{action_id}"
                )
            }
        )

    def mutate_customer_conversion_goal(
        self,
        resource_name: str,
        *,
        biddable: bool,
        validate_only: bool,
    ) -> dict[str, str | bool]:
        self.goal_mutations.append((resource_name, biddable, validate_only))
        return {"validated": True} if validate_only else {
            "resourceName": resource_name
        }


def google_inventory(
    actions: list[dict[str, object]] | None = None,
    *,
    custom_goals: list[dict[str, object]] | None = None,
    customer_goal_biddable: bool = False,
    campaign_goal_biddable: bool = False,
) -> google_setup.GoogleInventory:
    action_rows = actions or []
    pairs = {
        (
            row["conversionAction"]["category"],
            row["conversionAction"]["origin"],
        )
        for row in action_rows
    }
    return google_setup.GoogleInventory.from_search_rows(
        actions=action_rows,
        customer_goals=[
            {
                "customerConversionGoal": {
                    "resourceName": (
                        f"customers/{google_setup.CUSTOMER_ID}/"
                        f"customerConversionGoals/{category}~{origin}"
                    ),
                    "category": category,
                    "origin": origin,
                    "biddable": customer_goal_biddable,
                }
            }
            for category, origin in pairs
        ],
        campaign_goals=[
            {
                "campaignConversionGoal": {
                    "resourceName": (
                        f"customers/{google_setup.CUSTOMER_ID}/campaignConversionGoals/"
                        f"1~{category}~{origin}"
                    ),
                    "category": category,
                    "origin": origin,
                    "biddable": campaign_goal_biddable,
                }
            }
            for category, origin in pairs
        ],
        custom_goals=custom_goals or [],
        campaign_configs=[],
    )


class GooglePlatformSetupTests(unittest.TestCase):
    def test_create_shape_is_secondary_upload_clicks_with_no_goal_mutation(self) -> None:
        spec = google_setup.PLANNED_ACTIONS[0]
        request = google_setup.conversion_action_mutate_request(
            spec,
            validate_only=True,
        )
        create = request["operations"][0]["create"]

        self.assertEqual("UPLOAD_CLICKS", create["type"])
        self.assertEqual("BOOK_APPOINTMENT", create["category"])
        self.assertFalse(create["primaryForGoal"])
        self.assertEqual("ONE_PER_CLICK", create["countingType"])
        self.assertNotIn("valueSettings", create)
        self.assertTrue(request["validateOnly"])

    def test_apply_validates_each_missing_action_before_real_mutate(self) -> None:
        after_actions = [
            google_action_row(spec, str(8000 + index))
            for index, spec in enumerate(google_setup.PLANNED_ACTIONS)
        ]
        client = FakeGoogleClient(
            google_inventory(),
            google_inventory(after_actions),
        )

        report = google_setup.reconcile_google_actions(client, mode="apply")

        for spec in google_setup.PLANNED_ACTIONS:
            positions = [
                index
                for index, call in enumerate(client.mutations)
                if call[0] == spec.name
            ]
            self.assertEqual(2, len(positions))
            self.assertTrue(client.mutations[positions[0]][1])
            self.assertFalse(client.mutations[positions[1]][1])
        self.assertEqual(0, report["goal_mutations"])
        self.assertEqual(
            {"created_and_verified"},
            {row["status"] for row in report["actions"]},
        )
        self.assertTrue(
            all(str(row["action_id"]).isdigit() for row in report["actions"])
        )

    def test_apply_disables_exclusive_generated_customer_goals(self) -> None:
        actions = [
            google_action_row(spec, str(8050 + index))
            for index, spec in enumerate(google_setup.PLANNED_ACTIONS)
        ]
        client = FakeGoogleClient(
            google_inventory(actions, customer_goal_biddable=True),
            google_inventory(actions, customer_goal_biddable=True),
            google_inventory(actions, customer_goal_biddable=False),
        )

        report = google_setup.reconcile_google_actions(client, mode="apply")

        self.assertEqual(3, report["goal_mutations"])
        self.assertEqual(6, len(client.goal_mutations))
        self.assertTrue(all(call[1] is False for call in client.goal_mutations))
        self.assertEqual(
            [True, False, True, False, True, False],
            [call[2] for call in client.goal_mutations],
        )
        self.assertTrue(
            all(not row["customer_goal_biddable"] for row in report["actions"])
        )

    def test_shared_category_origin_goal_fails_closed(self) -> None:
        spec = google_setup.PLANNED_ACTIONS[0]
        planned = google_action_row(spec, "8090")
        shared = {
            "conversionAction": {
                **planned["conversionAction"],
                "resourceName": (
                    f"customers/{google_setup.CUSTOMER_ID}/conversionActions/8091"
                ),
                "id": "8091",
                "name": "Existing shared action",
            }
        }
        with self.assertRaisesRegex(google_setup.SetupError, "shares its"):
            google_setup.reconcile_google_actions(
                FakeGoogleClient(google_inventory([planned, shared])),
                mode="read_back",
            )

    def test_existing_exact_actions_are_idempotent(self) -> None:
        actions = [
            google_action_row(spec, str(8100 + index))
            for index, spec in enumerate(google_setup.PLANNED_ACTIONS)
        ]
        client = FakeGoogleClient(google_inventory(actions))

        report = google_setup.reconcile_google_actions(client, mode="read_back")

        self.assertEqual([], client.mutations)
        self.assertEqual(
            {"existing_match"},
            {row["status"] for row in report["actions"]},
        )

    def test_primary_or_custom_goal_inclusion_fails_closed(self) -> None:
        spec = google_setup.PLANNED_ACTIONS[0]
        with self.assertRaisesRegex(google_setup.SetupError, "primaryForGoal"):
            google_setup.reconcile_google_actions(
                FakeGoogleClient(
                    google_inventory([google_action_row(spec, "8200", primary=True)])
                ),
                mode="read_back",
            )

        resource_name = (
            f"customers/{google_setup.CUSTOMER_ID}/conversionActions/8201"
        )
        with self.assertRaisesRegex(google_setup.SetupError, "custom conversion goal"):
            google_setup.reconcile_google_actions(
                FakeGoogleClient(
                    google_inventory(
                        [google_action_row(spec, "8201")],
                        custom_goals=[
                            {
                                "customConversionGoal": {
                                    "id": "1",
                                    "name": "Existing bidding goal",
                                    "status": "ENABLED",
                                    "conversionActions": [resource_name],
                                }
                            }
                        ],
                    )
                ),
                mode="read_back",
            )


def meta_row(
    spec: meta_setup.PlannedCustomConversion,
    conversion_id: str,
    *,
    dataset_id: str = meta_setup.META_DATASET_ID,
    rule: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "id": conversion_id,
        "name": spec.name,
        "custom_event_type": meta_setup.CUSTOM_EVENT_TYPE,
        "pixel": {"id": dataset_id, "name": "CEFA's Pixel - NEW"},
        "is_archived": False,
        "is_unavailable": False,
        "rule": rule or meta_setup.conversion_rule(spec.event_name),
    }


class FakeMetaClient:
    account_id = f"act_{meta_setup.META_AD_ACCOUNT_ID}"

    def __init__(
        self,
        before: list[dict[str, object]],
        after: list[dict[str, object]] | None = None,
    ) -> None:
        self.inventories = [before, after if after is not None else before]
        self.inventory_calls = 0
        self.creates: list[tuple[str, str]] = []

    def inventory(self) -> list[dict[str, object]]:
        index = min(self.inventory_calls, len(self.inventories) - 1)
        self.inventory_calls += 1
        return self.inventories[index]

    def create(
        self,
        spec: meta_setup.PlannedCustomConversion,
        *,
        dataset_id: str,
    ) -> dict[str, str]:
        self.creates.append((spec.name, dataset_id))
        return {"id": str(7000 + len(self.creates))}


class MetaPlatformSetupTests(unittest.TestCase):
    def test_custom_conversion_rule_uses_only_the_approved_crm_event(self) -> None:
        spec = meta_setup.PLANNED_CONVERSIONS[0]
        create = meta_setup.custom_conversion_create(spec)

        self.assertEqual(meta_setup.META_DATASET_ID, create["event_source_id"])
        self.assertEqual("LEAD", create["custom_event_type"])
        self.assertEqual(
            {"and": [{"event": {"eq": "CEFA_CRM_TourScheduled"}}]},
            create["rule"],
        )

    def test_apply_creates_reporting_objects_and_reads_them_back(self) -> None:
        after = [
            meta_row(spec, str(7100 + index))
            for index, spec in enumerate(meta_setup.PLANNED_CONVERSIONS)
        ]
        client = FakeMetaClient([], after)

        report = meta_setup.reconcile_meta_conversions(client, mode="apply")

        self.assertEqual(3, len(client.creates))
        self.assertEqual(0, report["campaign_or_ad_set_mutations"])
        self.assertTrue(
            all(row["reporting_only"] for row in report["custom_conversions"])
        )
        self.assertEqual(
            {"created_and_verified"},
            {row["status"] for row in report["custom_conversions"]},
        )

    def test_existing_exact_meta_conversions_are_idempotent(self) -> None:
        existing = [
            meta_row(spec, str(7200 + index))
            for index, spec in enumerate(meta_setup.PLANNED_CONVERSIONS)
        ]
        client = FakeMetaClient(existing)

        report = meta_setup.reconcile_meta_conversions(client, mode="read_back")

        self.assertEqual([], client.creates)
        self.assertEqual(
            {"existing_match"},
            {row["status"] for row in report["custom_conversions"]},
        )

    def test_conflicting_meta_rule_fails_closed(self) -> None:
        spec = meta_setup.PLANNED_CONVERSIONS[0]
        existing = [
            meta_row(
                spec,
                "7300",
                rule={"and": [{"event": {"eq": "Inquiry Submit"}}]},
            )
        ]
        with self.assertRaisesRegex(meta_setup.SetupError, "conflicts"):
            meta_setup.reconcile_meta_conversions(
                FakeMetaClient(existing),
                mode="read_back",
            )


if __name__ == "__main__":
    unittest.main()
