from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "parent_activation" / "bigquery_store.py"
SPEC = importlib.util.spec_from_file_location("parent_activation_bigquery_store", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class FakeJob:
    def result(self) -> None:
        return None


class FakeBigQueryClient:
    def __init__(self) -> None:
        self.queries: list[tuple[str, object]] = []
        self.inserts: list[tuple[str, list[dict[str, object]]]] = []

    def query(self, query: str, job_config: object = None) -> FakeJob:
        self.queries.append((query, job_config))
        return FakeJob()

    def insert_rows_json(self, table: str, json_rows: object) -> list[object]:
        self.inserts.append((table, list(json_rows)))
        return []


class OutboxContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = FakeBigQueryClient()
        self.store = MODULE.ParentActivationBigQueryStore(
            self.client,
            transaction_secret=b"test-only-secret",
        )
        self.identity = MODULE.OutboxIdentity(
            form4_event_id="event-4f2a",
            canonical_stage="tour_scheduled",
            platform="google",
            destination_action_key="parent_crm_tour_scheduled_google",
        )

    def test_transaction_is_deterministic_for_the_dedupe_identity(self) -> None:
        first = MODULE.transaction_id_for(self.identity, b"test-only-secret")
        second = MODULE.transaction_id_for(self.identity, b"test-only-secret")
        self.assertEqual(first, second)

    def test_transaction_changes_when_platform_action_changes(self) -> None:
        meta_identity = MODULE.OutboxIdentity(
            form4_event_id=self.identity.form4_event_id,
            canonical_stage=self.identity.canonical_stage,
            platform="meta",
            destination_action_key="CEFA_CRM_TourScheduled",
        )
        self.assertNotEqual(
            MODULE.transaction_id_for(self.identity, b"test-only-secret"),
            MODULE.transaction_id_for(meta_identity, b"test-only-secret"),
        )

    def test_quarantined_row_cannot_be_queued(self) -> None:
        row = self.store.build_outbox_row(
            selected_lifecycle_event_id="lifecycle-1",
            identity=self.identity,
            activation_subject_id_hmac="lead-hmac",
            activation_identity_scope="form4_event",
            source_lifecycle_event_count=2,
            destination_account_id="4159217891",
            platform_event_name="CEFA | Parent | CRM Tour Scheduled | GOOGLE",
            event_time=datetime(2026, 7, 23, tzinfo=timezone.utc),
            match_key_ref=None,
            activation_mode="secondary_production",
            quarantine_reason="missing_exact_form4_identity",
        )
        self.assertEqual("blocked", row["delivery_status"])
        self.assertEqual(MODULE.QUARANTINED, row["quarantine_status"])
        self.assertIsNone(row["next_attempt_at"])

    def test_initial_snapshot_is_always_non_uploadable(self) -> None:
        self.store.write_initial_snapshot(
            [
                {
                    "snapshot_at": "2026-07-23T00:00:00Z",
                    "snapshot_date": "2026-07-23",
                    "poll_run_id": "baseline-1",
                    "opportunity_id_hmac": "opportunity-hmac",
                    "stage_mapping_version": "v1",
                    "has_gclid": False,
                    "has_gbraid": False,
                    "has_wbraid": False,
                    "has_fbc": False,
                    "has_fbp": False,
                    "has_email_hash": False,
                    "has_phone_hash": False,
                }
            ]
        )
        _, rows = self.client.inserts[0]
        self.assertTrue(rows[0]["is_initial_baseline"])
        self.assertEqual(MODULE.BASELINE_NON_UPLOADABLE, rows[0]["baseline_status"])

    def test_raw_pii_is_rejected_before_insert(self) -> None:
        with self.assertRaisesRegex(ValueError, "email"):
            self.store.write_lifecycle_event(
                {
                    "lifecycle_event_id": "lifecycle-1",
                    "email": "parent@example.com",
                }
            )

    def test_enqueue_merge_uses_event_stage_platform_and_action_dedupe(self) -> None:
        row = self.store.build_outbox_row(
            selected_lifecycle_event_id="lifecycle-1",
            identity=self.identity,
            activation_subject_id_hmac="lead-hmac",
            activation_identity_scope="form4_event",
            source_lifecycle_event_count=1,
            destination_account_id="4159217891",
            platform_event_name="CEFA | Parent | CRM Tour Scheduled | GOOGLE",
            event_time=datetime(2026, 7, 23, tzinfo=timezone.utc),
            match_key_ref="match-key-1",
            activation_mode="validate_only",
        )
        self.store.enqueue_outbox(row)
        query, job_config = self.client.queries[0]
        self.assertIn("MERGE", query)
        self.assertIn("target.form4_event_id = source.form4_event_id", query)
        self.assertIn("target.canonical_stage = source.canonical_stage", query)
        self.assertIn("target.platform = source.platform", query)
        self.assertIn("target.destination_action_key = source.destination_action_key", query)
        self.assertIn("target.accepted_at IS NULL", query)
        self.assertIsNotNone(job_config)

    def test_accepted_lock_prevents_reopen(self) -> None:
        self.store.mark_accepted("outbox-1", "google-request-1")
        query, _ = self.client.queries[0]
        self.assertIn("accepted_at IS NULL", query)
        self.assertIn("delivery_status = 'accepted'", query)

    def test_lease_excludes_quarantined_and_accepted_rows(self) -> None:
        self.store.lease_outbox("outbox-1", "worker-1", lease_seconds=120)
        query, _ = self.client.queries[0]
        self.assertIn("quarantine_status = 'not_quarantined'", query)
        self.assertIn("accepted_at IS NULL", query)
        self.assertIn("lease_expires_at <= CURRENT_TIMESTAMP()", query)
        self.assertIn("attempt_count = attempt_count + 1", query)

    def test_sql_contract_has_no_prohibited_raw_pii_columns(self) -> None:
        sql = (Path(__file__).resolve().parents[2] / "parent_crm_lifecycle_foundation.sql").read_text(encoding="utf-8")
        for column in MODULE.PROHIBITED_RAW_PII_COLUMNS:
            self.assertNotRegex(sql.lower(), rf"\b{column}\s+(string|timestamp|date)\b")
        self.assertIn("partition_expiration_days = 100", sql)


if __name__ == "__main__":
    unittest.main()
