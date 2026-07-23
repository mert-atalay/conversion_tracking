from __future__ import annotations

import unittest
from datetime import datetime, timezone

from parent_activation.config import CanonicalStage, TIMESTAMP_QUALITY_POLL_OBSERVED
from parent_activation.lifecycle import evaluate_snapshot
from parent_activation.models import CrmOpportunitySnapshot, Form4Identity, QuarantineReason


NOW = datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc)


def exact_identity(event_id: str = "evt-1", entry_id: str = "401") -> Form4Identity:
    return Form4Identity(event_id, entry_id, event_id, entry_id, 1)


def snapshot(
    phase: str,
    identity: Form4Identity | None = None,
    baseline: bool = False,
) -> CrmOpportunitySnapshot:
    return CrmOpportunitySnapshot(
        opportunity_id_hmac="opp-hmac-1",
        raw_phase=phase,
        observed_at=NOW,
        identity=identity or exact_identity(),
        school_uuid="school-1",
        is_initial_baseline=baseline,
    )


class LifecycleTests(unittest.TestCase):
    def test_uploadable_stage_is_exact_identity_and_poll_observed(self) -> None:
        decision = evaluate_snapshot(snapshot("Tour Scheduled"))
        self.assertTrue(decision.uploadable)
        assert decision.event
        self.assertEqual(CanonicalStage.TOUR_SCHEDULED, decision.stage)
        self.assertEqual(TIMESTAMP_QUALITY_POLL_OBSERVED, decision.event.timestamp_quality)

    def test_all_approved_stages_map_to_their_canonical_values(self) -> None:
        expected = {
            "tour scheduled": CanonicalStage.TOUR_SCHEDULED,
            "post tour": CanonicalStage.TOUR_COMPLETED_CANDIDATE,
            "enrollment (closed won)": CanonicalStage.CRM_CLOSED_WON,
        }
        for raw_phase, stage in expected.items():
            self.assertEqual(stage, evaluate_snapshot(snapshot(raw_phase)).stage)

    def test_known_non_positive_and_unknown_stages_are_quarantined(self) -> None:
        for phase in ("nurturing", "closed lost", "tour missed"):
            self.assertEqual(
                QuarantineReason.NON_UPLOADABLE_STAGE,
                evaluate_snapshot(snapshot(phase)).quarantine_reason,
            )
        self.assertEqual(QuarantineReason.UNMAPPED_STAGE, evaluate_snapshot(snapshot("Application")).quarantine_reason)

    def test_baseline_is_never_uploadable(self) -> None:
        decision = evaluate_snapshot(snapshot("tour scheduled", baseline=True))
        self.assertFalse(decision.uploadable)
        self.assertEqual(QuarantineReason.BASELINE_NON_UPLOADABLE, decision.quarantine_reason)

    def test_exact_event_identity_is_required_and_entry_conflicts_are_blocked(self) -> None:
        missing = Form4Identity(None, None, None, None, 0)
        conflict = Form4Identity("evt-1", "401", "evt-1", "402", 1)
        ambiguous = Form4Identity("evt-1", "401", "evt-1", "401", 2)
        self.assertEqual(QuarantineReason.MISSING_FORM4_EVENT_ID, evaluate_snapshot(snapshot("tour scheduled", missing)).quarantine_reason)
        self.assertEqual(QuarantineReason.CONFLICTING_FORM_ENTRY_ID, evaluate_snapshot(snapshot("tour scheduled", conflict)).quarantine_reason)
        self.assertEqual(QuarantineReason.AMBIGUOUS_FORM4_IDENTITY, evaluate_snapshot(snapshot("tour scheduled", ambiguous)).quarantine_reason)

    def test_first_positive_stage_only(self) -> None:
        decision = evaluate_snapshot(
            snapshot("post tour"),
            {("evt-1", CanonicalStage.TOUR_COMPLETED_CANDIDATE)},
        )
        self.assertFalse(decision.uploadable)
        self.assertEqual(QuarantineReason.FIRST_POSITIVE_OCCURRENCE_ALREADY_SENT, decision.quarantine_reason)


if __name__ == "__main__":
    unittest.main()
