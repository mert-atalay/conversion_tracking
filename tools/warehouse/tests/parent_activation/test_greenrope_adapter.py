from __future__ import annotations

from datetime import datetime, timezone
import unittest

from parent_activation.greenrope_adapter import (
    GreenRopeClient,
    as_unresolved_form4_identity,
    compare_to_previous,
    parse_opportunity,
)
from parent_activation.lifecycle import evaluate_snapshot
from parent_activation.models import CrmOpportunitySnapshot, Form4Identity, QuarantineReason


OPPORTUNITY = {
    "opportunity_id": "synthetic-opportunity-1",
    "phase": "Tour Scheduled",
    "email": "Parent@Example.COM ",
    "phone": "(604) 555-0100",
    "customfields": {
        "customfield": [
            {"fieldname": "CEFA Event ID", "fieldvalue": "event-1"},
            {"fieldname": "CEFA Form Entry ID", "fieldvalue": "entry-44"},
            {"fieldname": "School UUID", "fieldvalue": "school-123"},
            {"fieldname": "gclid", "fieldvalue": "real-gclid"},
            {"fieldname": "gbraid", "fieldvalue": "real-gbraid"},
            {"fieldname": "wbraid", "fieldvalue": "real-wbraid"},
            {"fieldname": "fbclid", "fieldvalue": "real-fbclid"},
            {"fieldname": "fbc", "fieldvalue": "fb.1.real"},
            {"fieldname": "fbp", "fieldvalue": "fb.1.cookie"},
            {"fieldname": "UTM Source", "fieldvalue": "google"},
        ]
    },
}


class GreenRopeAdapterTests(unittest.TestCase):
    def test_parse_uses_exact_identity_and_never_returns_raw_contact_values(self) -> None:
        parsed = parse_opportunity(OPPORTUNITY, group_id="group-1", hmac_secret="test-secret")

        self.assertEqual("event-1", parsed.form4_event_id)
        self.assertEqual("entry-44", parsed.form_entry_id)
        self.assertEqual("real-gclid", parsed.match_values.gclid)
        self.assertEqual("real-gbraid", parsed.match_values.gbraid)
        self.assertEqual("real-wbraid", parsed.match_values.wbraid)
        self.assertEqual("real-fbclid", parsed.match_values.fbclid)
        self.assertEqual("fb.1.real", parsed.match_values.fbc)
        self.assertEqual("fb.1.cookie", parsed.match_values.fbp)
        self.assertEqual(64, len(parsed.match_values.email_sha256 or ""))
        self.assertEqual(64, len(parsed.match_values.phone_sha256 or ""))
        self.assertNotIn("email", parsed.state_record())
        self.assertNotIn("phone", parsed.state_record())
        self.assertNotIn("Parent@Example.COM", repr(parsed))
        self.assertNotIn("604) 555", repr(parsed))

    def test_first_snapshot_is_baseline_then_changed_phase_is_poll_observed(self) -> None:
        before = parse_opportunity(OPPORTUNITY, group_id="group-1", hmac_secret="test-secret")
        observed_at = datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc)
        baseline = compare_to_previous([before], {}, observed_at=observed_at, baseline=True)
        self.assertTrue(baseline[0].is_initial_baseline)
        self.assertFalse(baseline[0].phase_changed)

        changed_source = dict(OPPORTUNITY, phase="Post Tour")
        changed = parse_opportunity(changed_source, group_id="group-1", hmac_secret="test-secret")
        poll = compare_to_previous(
            [changed],
            {before.opportunity_id_hmac: before.state_record()},
            observed_at=observed_at,
            baseline=False,
        )
        self.assertTrue(poll[0].phase_changed)
        self.assertFalse(poll[0].is_initial_baseline)

        unresolved = CrmOpportunitySnapshot(
            opportunity_id_hmac=changed.opportunity_id_hmac,
            raw_phase=changed.raw_phase,
            observed_at=observed_at,
            identity=as_unresolved_form4_identity(changed),
        )
        self.assertEqual(QuarantineReason.AMBIGUOUS_FORM4_IDENTITY, evaluate_snapshot(unresolved).quarantine_reason)

        resolved = CrmOpportunitySnapshot(
            opportunity_id_hmac=changed.opportunity_id_hmac,
            raw_phase=changed.raw_phase,
            observed_at=observed_at,
            identity=Form4Identity("event-1", "entry-44", "event-1", "entry-44", 1),
        )
        decision = evaluate_snapshot(resolved)
        self.assertTrue(decision.uploadable)
        self.assertEqual("tour_completed_candidate", decision.stage)
        self.assertEqual("poll_observed", decision.event.timestamp_quality if decision.event else None)

    def test_client_retries_read_only_request_without_exposing_response(self) -> None:
        calls = 0

        def transport(request: object, _: int) -> dict[str, object]:
            nonlocal calls
            calls += 1
            if calls == 1:
                from urllib.error import URLError

                raise URLError("temporary")
            return {"GetGroupsResponse": {"groups": {"group": {"group_id": "1", "name": "Synthetic"}}}}

        client = GreenRopeClient(
            "https://example.invalid", "email", "token", "account", sleep=lambda _: None, transport=transport
        )
        self.assertEqual([{"id": "1", "name": "Synthetic"}], client.groups())
        self.assertEqual(2, calls)


if __name__ == "__main__":
    unittest.main()
