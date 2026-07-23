from __future__ import annotations

import hashlib
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from parent_activation import bigquery_store as store_module
from parent_activation.config import ConsentState
from parent_activation.google_datamanager import GoogleMatchKeys, build_google_event
from parent_activation.meta_capi import MetaMatchKeys, build_meta_event


class FakeJob:
    def __init__(self, affected_rows: int = 1) -> None:
        self.num_dml_affected_rows = affected_rows

    def result(self) -> None:
        return None


class FakeBigQueryClient:
    def __init__(self) -> None:
        self.queries: list[tuple[str, object]] = []
        self.inserts: list[tuple[str, list[dict[str, object]]]] = []
        self.next_affected_rows = 1

    def query(self, query: str, job_config: object = None) -> FakeJob:
        self.queries.append((query, job_config))
        return FakeJob(self.next_affected_rows)

    def insert_rows_json(self, table: str, json_rows: object) -> list[object]:
        self.inserts.append((table, list(json_rows)))
        return []


class OutboxContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = FakeBigQueryClient()
        self.store = store_module.ParentActivationBigQueryStore(
            self.client,
            transaction_secret=b"test-only-secret",
        )
        self.identity = store_module.OutboxIdentity(
            form4_event_id="event-4f2a",
            canonical_stage="tour_scheduled",
            platform="google",
            destination_action_key="parent_crm_tour_scheduled_google",
        )
        self.event_at = datetime(2026, 7, 23, 12, tzinfo=timezone.utc)

    def build_row(
        self,
        *,
        baseline: bool = False,
        quarantine_reason: str | None = None,
        platform: str = "google",
        action_key: str = "parent_crm_tour_scheduled_google",
    ) -> dict[str, object]:
        identity = store_module.OutboxIdentity(
            form4_event_id=self.identity.form4_event_id,
            canonical_stage=self.identity.canonical_stage,
            platform=platform,
            destination_action_key=action_key,
        )
        return self.store.build_outbox_row(
            selected_lifecycle_event_id="lifecycle-1",
            identity=identity,
            activation_subject_id_hmac="c" * 64,
            activation_identity_scope="form4_event",
            source_lifecycle_event_count=1,
            source_is_initial_baseline=baseline,
            school_uuid="school-uuid-1",
            destination_account_id=(
                "4159217891" if platform == "google" else "918227085392601"
            ),
            platform_event_name=(
                "CEFA Parent CRM Tour Scheduled"
                if platform == "google"
                else "CEFA_CRM_TourScheduled"
            ),
            event_timestamp=self.event_at,
            match_key_ref="match-key-1",
            activation_mode="validate_only",
            quarantine_reason=quarantine_reason,
        )

    def test_transaction_is_deterministic_and_platform_scoped(self) -> None:
        first = store_module.transaction_id_for(
            self.identity,
            b"test-only-secret",
        )
        second = store_module.transaction_id_for(
            self.identity,
            b"test-only-secret",
        )
        meta_identity = store_module.OutboxIdentity(
            form4_event_id=self.identity.form4_event_id,
            canonical_stage=self.identity.canonical_stage,
            platform="meta",
            destination_action_key="CEFA_CRM_TourScheduled",
        )
        self.assertEqual(first, second)
        self.assertNotEqual(
            first,
            store_module.transaction_id_for(
                meta_identity,
                b"test-only-secret",
            ),
        )

    def test_initial_snapshot_and_lifecycle_are_always_non_uploadable(self) -> None:
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
        _, snapshot_rows = self.client.inserts[0]
        self.assertTrue(snapshot_rows[0]["is_initial_baseline"])
        self.assertEqual(
            store_module.BASELINE_NON_UPLOADABLE,
            snapshot_rows[0]["baseline_status"],
        )

        self.store.write_lifecycle_event(
            {
                "lifecycle_event_id": "lifecycle-baseline",
                "is_initial_baseline": True,
                "eligibility_status": "eligible",
            }
        )
        _, lifecycle_rows = self.client.inserts[1]
        self.assertEqual(
            store_module.BASELINE_NON_UPLOADABLE,
            lifecycle_rows[0]["eligibility_status"],
        )
        self.assertEqual(
            store_module.BASELINE_NON_UPLOADABLE,
            lifecycle_rows[0]["quarantine_reason"],
        )

    def test_baseline_outbox_is_blocked_and_cannot_be_forged_queueable(self) -> None:
        row = self.build_row(baseline=True)
        self.assertEqual("blocked", row["delivery_status"])
        self.assertEqual(
            store_module.BASELINE_NON_UPLOADABLE,
            row["quarantine_reason"],
        )
        self.assertIsNone(row["next_attempt_at"])
        forged = dict(row)
        forged["delivery_status"] = "queued"
        with self.assertRaisesRegex(ValueError, "baseline outbox"):
            self.store.enqueue_outbox(forged)

    def test_outbox_fields_feed_google_and_meta_adapters_directly(self) -> None:
        google_row = self.build_row()
        email_hash = hashlib.sha256(b"parent@example.com").hexdigest()
        google_event = build_google_event(
            google_row,
            GoogleMatchKeys(
                gclid="real-gclid",
                click_id_captured_at=self.event_at - timedelta(days=1),
                email_sha256=email_hash,
                user_data_captured_at=self.event_at - timedelta(days=1),
                consent_state=ConsentState.GRANTED,
            ),
        )
        self.assertEqual(google_row["transaction_id"], google_event["transactionId"])

        meta_row = self.build_row(
            platform="meta",
            action_key="CEFA_CRM_TourScheduled",
        )
        meta_event = build_meta_event(
            meta_row,
            MetaMatchKeys(
                external_id="d" * 64,
                email_sha256=email_hash,
                consent_state=ConsentState.GRANTED,
            ),
            now=self.event_at,
        )
        self.assertEqual(meta_row["transaction_id"], meta_event["event_id"])
        self.assertEqual(meta_row["school_uuid"], meta_event["custom_data"]["school_uuid"])

    def test_recursive_pii_and_log_guards_redact_before_insert(self) -> None:
        with self.assertRaisesRegex(ValueError, "Contact.Email"):
            self.store.write_lifecycle_event(
                {
                    "lifecycle_event_id": "lifecycle-1",
                    "nested": {"Contact.Email": "parent@example.com"},
                }
            )
        with self.assertRaisesRegex(ValueError, "PII-like"):
            store_module.assert_no_prohibited_raw_pii(
                {"diagnostic": "parent@example.com"}
            )
        store_module.assert_no_prohibited_raw_pii(
            {
                "poll_run_id": "29661474-3a63-4878-9698-7a1912bffb7f",
                "school_uuid": "65d378e6-8f10-41f6-8335-8282c07e44b1",
            }
        )
        with self.assertRaisesRegex(ValueError, "PII-like"):
            store_module.assert_no_prohibited_raw_pii(
                {"diagnostic": "29661474-3a63-4878-9698-7a1912bffb7f"}
            )
        self.store.record_delivery_attempt(
            {
                "delivery_attempt_id": "attempt-1",
                "error_message": "Rejected parent@example.com or +1 (604) 555-0100",
            }
        )
        _, rows = self.client.inserts[-1]
        self.assertNotIn("parent@example.com", rows[0]["error_message"])
        self.assertNotIn("604", rows[0]["error_message"])

    def test_identifier_formats_are_constrained(self) -> None:
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            self.store.build_outbox_row(
                selected_lifecycle_event_id="lifecycle-1",
                identity=self.identity,
                activation_subject_id_hmac="native-crm-id",
                activation_identity_scope="form4_event",
                source_lifecycle_event_count=1,
                source_is_initial_baseline=False,
                school_uuid="school-uuid-1",
                destination_account_id="4159217891",
                platform_event_name="test",
                event_timestamp=self.event_at,
                match_key_ref=None,
                activation_mode="validate_only",
            )
        with self.assertRaisesRegex(ValueError, "opaque"):
            store_module.transaction_id_for(
                store_module.OutboxIdentity(
                    "parent@example.com",
                    "tour_scheduled",
                    "google",
                    "action",
                ),
                b"secret",
            )

    def test_enqueue_dedupe_and_lease_are_atomic_and_baseline_aware(self) -> None:
        self.store.enqueue_outbox(self.build_row())
        merge_query, job_config = self.client.queries[0]
        self.assertIn("target.form4_event_id = source.form4_event_id", merge_query)
        self.assertIn("target.canonical_stage = source.canonical_stage", merge_query)
        self.assertIn("target.platform = source.platform", merge_query)
        self.assertIn("target.destination_action_key = source.destination_action_key", merge_query)
        self.assertIn("target.delivery_status NOT IN ('leased', 'permanent_failure')", merge_query)
        self.assertIsNotNone(job_config)

        self.assertTrue(self.store.lease_outbox("outbox-1", "worker-1", 120))
        lease_query, _ = self.client.queries[1]
        self.assertIn("source_is_initial_baseline = FALSE", lease_query)
        self.assertIn("attempt_count = attempt_count + 1", lease_query)
        self.client.next_affected_rows = 0
        self.assertFalse(self.store.lease_outbox("outbox-1", "worker-2", 120))

    def test_final_transitions_require_same_unexpired_lease_owner(self) -> None:
        self.assertTrue(
            self.store.mark_accepted(
                "outbox-1",
                "worker-1",
                "google-request-1",
            )
        )
        query, _ = self.client.queries[-1]
        self.assertIn("lease_owner = @worker_id", query)
        self.assertIn("lease_expires_at > CURRENT_TIMESTAMP()", query)
        self.assertIn("delivery_status = 'leased'", query)

        self.assertTrue(
            self.store.mark_retryable_failure(
                "outbox-2",
                "worker-1",
                error_code="temporary_error",
                error_message="retry parent@example.com",
                next_attempt_at=self.event_at + timedelta(minutes=5),
            )
        )
        retry_parameters = self.client.queries[-1][1].query_parameters
        rendered = {parameter.name: parameter.value for parameter in retry_parameters}
        self.assertNotIn("parent@example.com", rendered["error_message"])

        self.assertTrue(
            self.store.mark_permanent_failure(
                "outbox-3",
                "worker-1",
                error_code="invalid_destination",
                error_message="not retryable",
            )
        )
        self.assertTrue(self.store.release_lease("outbox-4", "worker-1"))

    def test_sql_uses_only_new_restricted_dataset_and_no_dashboard_objects(self) -> None:
        sql = (
            Path(__file__).resolve().parents[2]
            / "parent_crm_lifecycle_foundation.sql"
        ).read_text(encoding="utf-8")
        self.assertIn("cefa_parent_activation_restricted", sql)
        self.assertNotIn("`marketing-api-488017.cefa_restricted", sql)
        self.assertNotIn("mart_cefa_growth_dashboard", sql)
        self.assertNotIn("CREATE OR REPLACE VIEW", sql)
        self.assertIn("partition_expiration_days = 100", sql)
        self.assertIn("source_is_initial_baseline BOOL NOT NULL", sql)
        self.assertIn("event_timestamp TIMESTAMP NOT NULL", sql)
        for column in store_module.PROHIBITED_RAW_PII_COLUMNS:
            self.assertNotRegex(
                sql.lower(),
                rf"\b{column}\s+(string|timestamp|date)\b",
            )


if __name__ == "__main__":
    unittest.main()
