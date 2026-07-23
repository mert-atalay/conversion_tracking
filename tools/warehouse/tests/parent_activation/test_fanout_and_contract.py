from __future__ import annotations

import dataclasses
import unittest
from datetime import datetime, timedelta, timezone

from parent_activation.lifecycle import collapse_multi_school_fanout, evaluate_snapshot
from parent_activation.models import CrmOpportunitySnapshot, Form4Identity, LifecycleEvent, QuarantineReason


class FanoutAndContractTests(unittest.TestCase):
    def test_multi_school_fanout_collapses_to_the_earliest_opportunity(self) -> None:
        identity = Form4Identity("evt-9", "900", "evt-9", "900", 1)
        earlier = CrmOpportunitySnapshot(
            "opp-a", "tour scheduled", datetime(2026, 7, 23, tzinfo=timezone.utc), identity, "school-a"
        )
        later = CrmOpportunitySnapshot(
            "opp-b", "tour scheduled", datetime(2026, 7, 23, tzinfo=timezone.utc) + timedelta(minutes=1), identity, "school-b"
        )
        results = collapse_multi_school_fanout([evaluate_snapshot(later), evaluate_snapshot(earlier)])
        uploadable = [result for result in results if result.uploadable]
        collapsed = [result for result in results if result.quarantine_reason == QuarantineReason.MULTI_SCHOOL_FANOUT_COLLAPSED]
        self.assertEqual(1, len(uploadable))
        self.assertEqual("opp-a", uploadable[0].event.opportunity_id_hmac if uploadable[0].event else None)
        self.assertEqual(1, len(collapsed))

    def test_persistent_model_contract_has_no_raw_contact_fields(self) -> None:
        prohibited = {"email", "phone", "name", "address", "ip_address", "raw_payload"}
        for model in (CrmOpportunitySnapshot, Form4Identity, LifecycleEvent):
            self.assertFalse(prohibited.intersection(field.name for field in dataclasses.fields(model)))


if __name__ == "__main__":
    unittest.main()
