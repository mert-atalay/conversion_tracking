from __future__ import annotations

from datetime import datetime, timezone
from unittest import TestCase, mock

from parent_activation.bigquery_store import ParentActivationBigQueryStore
from parent_activation.config import ConsentState
from parent_activation.dispatcher import dispatch_due
from parent_activation.greenrope_adapter import (
    ParsedOpportunity,
    PlatformMatchValues,
    PollObservation,
)
from parent_activation.models import Form4Identity, QuarantineReason
from parent_activation.poller_runtime import (
    build_and_enqueue_outbox,
    build_lifecycle_decisions,
    build_snapshot_rows,
)
from parent_activation.repository import Form4Match


NOW = datetime(2026, 7, 23, 20, 0, tzinfo=timezone.utc)
EVENT_ID = "cefa-parent-event-123"
ENTRY_ID = "456"
SCHOOL_UUID = "65d378e6-8f10-41f6-8335-8282c07e44b1"
SHA = "a" * 64


def opportunity(*, phase: str = "tour scheduled") -> ParsedOpportunity:
    return ParsedOpportunity(
        opportunity_id_hmac="b" * 64,
        group_id="17",
        raw_phase=phase,
        form4_event_id=EVENT_ID,
        form_entry_id=ENTRY_ID,
        school_uuid=None,
        utm_source="google",
        utm_medium="cpc",
        utm_campaign="parent",
        utm_term=None,
        utm_content=None,
        match_values=PlatformMatchValues(
            email_sha256=SHA,
            phone_sha256=None,
            gclid="abcde_12345",
            gbraid=None,
            wbraid=None,
            fbclid=None,
            fbc=None,
            fbp=None,
        ),
    )


def exact_match(*, is_test: bool = False) -> Form4Match:
    return Form4Match(
        identity=Form4Identity(EVENT_ID, ENTRY_ID, EVENT_ID, ENTRY_ID, 1),
        school_uuid=SCHOOL_UUID,
        submitted_at=NOW,
        is_test=is_test,
        gclid="abcde_12345",
        gbraid=None,
        wbraid=None,
    )


class CaptureStore:
    def __init__(self) -> None:
        self.builder = ParentActivationBigQueryStore(
            client=object(),
            transaction_secret=b"test-secret",
        )
        self.rows: list[dict[str, object]] = []

    def build_outbox_row(self, **kwargs):
        return self.builder.build_outbox_row(**kwargs)

    def enqueue_outbox(self, row):
        self.rows.append(dict(row))


class CaptureRepository:
    def __init__(self) -> None:
        self.match_rows: list[dict[str, object]] = []

    def upsert_match_key(self, row):
        self.match_rows.append(dict(row))


class ParentPollRuntimeTest(TestCase):
    def test_first_seen_post_activation_state_is_still_non_uploadable(self) -> None:
        rows = build_snapshot_rows(
            [opportunity()],
            observed_at=NOW,
            poll_run_id="run-1",
            baseline=False,
            previous_state={},
        )
        self.assertTrue(rows[0]["is_initial_baseline"])
        self.assertEqual("baseline_non_uploadable", rows[0]["baseline_status"])

    def test_exact_identity_builds_one_uploadable_decision(self) -> None:
        item = opportunity()
        decisions = build_lifecycle_decisions(
            [
                PollObservation(
                    opportunity=item,
                    observed_at=NOW,
                    is_initial_baseline=False,
                    phase_changed=True,
                )
            ],
            {EVENT_ID: exact_match()},
        )
        self.assertEqual(1, len(decisions))
        self.assertTrue(decisions[0].uploadable)
        self.assertEqual(SCHOOL_UUID, decisions[0].snapshot.school_uuid)

    def test_controlled_test_record_never_builds_an_activation_event(self) -> None:
        item = opportunity()
        decisions = build_lifecycle_decisions(
            [
                PollObservation(
                    opportunity=item,
                    observed_at=NOW,
                    is_initial_baseline=False,
                    phase_changed=True,
                )
            ],
            {EVENT_ID: exact_match(is_test=True)},
        )
        self.assertFalse(decisions[0].uploadable)
        self.assertEqual(QuarantineReason.TEST_RECORD, decisions[0].quarantine_reason)

    def test_unknown_consent_quarantines_both_platform_rows(self) -> None:
        item = opportunity()
        decisions = build_lifecycle_decisions(
            [
                PollObservation(
                    opportunity=item,
                    observed_at=NOW,
                    is_initial_baseline=False,
                    phase_changed=True,
                )
            ],
            {EVENT_ID: exact_match()},
        )
        repository = CaptureRepository()
        store = CaptureStore()
        count = build_and_enqueue_outbox(
            decisions,
            {item.opportunity_id_hmac: item},
            {EVENT_ID: exact_match()},
            repository=repository,
            store=store,
            secret=b"test-secret",
            activation_mode="secondary_production",
            consent=ConsentState.UNKNOWN,
            google_destinations={"tour_scheduled": "123456789"},
            observed_at=NOW,
        )
        self.assertEqual(2, count)
        self.assertEqual(1, len(repository.match_rows))
        self.assertEqual(
            {"consent_unknown"},
            {row["quarantine_reason"] for row in store.rows},
        )


class FakeDispatchRepository:
    def __init__(self, rows, match):
        self.rows = rows
        self.match = match

    def due_outbox_rows(self, *, limit):
        return self.rows[:limit]

    def match_key(self, form4_event_id):
        return self.match


class FakeDispatchStore:
    def __init__(self):
        self.attempts = []
        self.released = 0

    def lease_outbox(self, outbox_id, worker_id, lease_seconds):
        return True

    def record_delivery_attempt(self, row):
        self.attempts.append(row)

    def release_lease(self, outbox_id, worker_id):
        self.released += 1
        return True


class ParentDispatcherTest(TestCase):
    def test_disabled_mode_does_not_read_or_send(self) -> None:
        repository = mock.Mock()
        summary = dispatch_due(
            repository=repository,
            store=mock.Mock(),
            mode="disabled",
        )
        self.assertEqual(0, summary.inspected)
        repository.due_outbox_rows.assert_not_called()

    def test_dry_run_records_no_platform_call(self) -> None:
        row = {
            "outbox_id": "c" * 64,
            "transaction_id": "d" * 64,
            "platform": "google",
            "destination_action_key": "123456789",
            "activation_mode": "dry_run",
            "form4_event_id": EVENT_ID,
            "attempt_count": 0,
        }
        repository = FakeDispatchRepository([row], {"consent_status": "granted"})
        store = FakeDispatchStore()
        with mock.patch(
            "parent_activation.dispatcher.ingest_google_events"
        ) as google_send:
            summary = dispatch_due(
                repository=repository,
                store=store,
                mode="dry_run",
                now=NOW,
            )
        google_send.assert_not_called()
        self.assertEqual(1, summary.leased)
        self.assertEqual(1, store.released)
        self.assertEqual("dry_run_ready", store.attempts[0]["delivery_status"])
