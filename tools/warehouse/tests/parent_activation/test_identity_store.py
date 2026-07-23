from __future__ import annotations

import unittest
from datetime import datetime, timezone
from typing import Any

from parent_activation.identity_store import ParentIdentityBigQueryStore


class _Job:
    num_dml_affected_rows = 1

    def result(self) -> list[object]:
        return []


class _Client:
    def __init__(self) -> None:
        self.query_text = ""

    def query(self, query: str, job_config: Any = None) -> _Job:
        self.query_text = query
        return _Job()


class IdentityStoreTests(unittest.TestCase):
    def test_overlap_upsert_preserves_binder_state(self) -> None:
        client = _Client()
        store = ParentIdentityBigQueryStore(client)
        now = datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc)
        store.upsert_identity(
            {
                "form4_event_id": "evt-test-1",
                "form_entry_id": "123",
                "school_uuid": "school-test",
                "greenrope_group_id": "5",
                "submitted_at": now.isoformat(),
                "assigned_email_hmac": "a" * 64,
                "assigned_phone_hmac": None,
                "parent_first_hmac": "b" * 64,
                "parent_last_hmac": "c" * 64,
                "child_dob_hmac": "d" * 64,
                "program_hmac": "e" * 64,
                "requested_start_hmac": "f" * 64,
                "consent_signal_status": "unknown",
                "bridge_status": "captured",
                "quarantine_reason": None,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
            }
        )

        self.assertIn("bridge_status = target.bridge_status", client.query_text)
        self.assertIn(
            "quarantine_reason = target.quarantine_reason",
            client.query_text,
        )
        self.assertNotIn("bridge_status = IF(", client.query_text)


if __name__ == "__main__":
    unittest.main()
