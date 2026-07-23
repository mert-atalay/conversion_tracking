from __future__ import annotations

from dataclasses import dataclass
import unittest

from parent_activation.identity_binder import run_identity_binder
from parent_activation.identity_bridge import SchoolBinding, build_identity_record
from datetime import datetime, timezone


SECRET = b"unit-test-secret"
SCHOOL_UUID = "81237895-bcad-11ef-8bcb-028d36469a89"


@dataclass(frozen=True)
class Field:
    normalized_label: str


class FakeStore:
    def __init__(self, row: dict[str, object]) -> None:
        self.row = row
        self.states: list[dict[str, object]] = []

    def pending_identities(self, *, limit: int = 500) -> list[dict[str, object]]:
        return [self.row]

    def record_match_state(self, **kwargs: object) -> bool:
        self.states.append(dict(kwargs))
        return True


class FakeClient:
    account_id = "account-1"

    def __init__(self, fields: list[str], opportunity: dict[str, object]) -> None:
        self._fields = fields
        self._opportunity = opportunity

    def opportunity_fields(self) -> list[Field]:
        return [Field(value) for value in self._fields]

    def opportunities(self, group_id: str) -> list[dict[str, object]]:
        return [self._opportunity]


def identity() -> dict[str, object]:
    return build_identity_record(
        {
            "form_id": "4",
            "entry_id": "8017",
            "submitted_at": "2026-07-23T12:00:00Z",
            "event_id": "cefa-parent-event-8017",
            "school_uuid": SCHOOL_UUID,
            "parent_first": "Example",
            "parent_last": "Parent",
            "email": "parent@example.com",
            "phone": "6045550100",
            "child_dob": "2023-03-04",
            "program": "Junior Kindergarten",
            "requested_start": "2026-09-01",
        },
        secret=SECRET,
        school_bindings={
            SCHOOL_UUID: SchoolBinding(
                SCHOOL_UUID,
                "surrey-campbell-heights",
                "Surrey - Campbell Heights",
                "58",
            )
        },
        received_at=datetime(2026, 7, 23, 12, 1, tzinfo=timezone.utc),
    )


def opportunity(
    *,
    current_event_id: str | None = None,
    current_entry_id: str | None = None,
) -> dict[str, object]:
    custom_fields = [
        {"fieldname": "child_dob", "fieldvalue": "2023-03-04"},
        {"fieldname": "program_name", "fieldvalue": "Junior Kindergarten"},
        {"fieldname": "requested_start_date", "fieldvalue": "2026-09-01"},
    ]
    if current_event_id:
        custom_fields.append(
            {"fieldname": "cefa_event_id", "fieldvalue": current_event_id}
        )
    if current_entry_id:
        custom_fields.append(
            {
                "fieldname": "cefa_form_entry_id",
                "fieldvalue": current_entry_id,
            }
        )
    return {
        "opportunity_id": "greenrope-1",
        "createdate": "2026-07-23 12:05:00",
        "quality": "5",
        "closedate": "2026-12-31",
        "assignedtoemail": "parent@example.com",
        "assignedtomobile": "6045550100",
        "assignedtofirstname": "Example",
        "assignedtolastname": "Parent",
        "customfields": {"customfield": custom_fields},
    }


class IdentityBinderTests(unittest.TestCase):
    def test_missing_new_greenrope_candidate_remains_retryable(self) -> None:
        store = FakeStore(identity())
        client = FakeClient([], opportunity())
        client._opportunity = {
            **opportunity(),
            "assignedtoemail": "different@example.com",
        }
        result = run_identity_binder(
            store=store,
            client=client,
            hmac_secret=SECRET,
            write_enabled=False,
        )

        self.assertEqual(1, result.retryable_failures)
        self.assertEqual("retryable_failure", store.states[0]["bridge_status"])
        self.assertEqual(
            "greenrope_candidate_not_yet_available",
            store.states[0]["quarantine_reason"],
        )

    def test_matching_runs_but_write_waits_for_greenrope_fields(self) -> None:
        store = FakeStore(identity())
        result = run_identity_binder(
            store=store,
            client=FakeClient([], opportunity()),
            hmac_secret=SECRET,
            write_enabled=False,
        )

        self.assertFalse(result.field_contract_ready)
        self.assertEqual(1, result.awaiting_fields)
        self.assertEqual("awaiting_greenrope_fields", store.states[0]["bridge_status"])

    def test_ready_fields_still_respect_write_kill_switch(self) -> None:
        store = FakeStore(identity())
        result = run_identity_binder(
            store=store,
            client=FakeClient(
                ["cefaeventid", "cefaformentryid"],
                opportunity(),
            ),
            hmac_secret=SECRET,
            write_enabled=False,
        )

        self.assertTrue(result.field_contract_ready)
        self.assertEqual(1, result.matched)
        self.assertEqual("matched", store.states[0]["bridge_status"])

    def test_conflicting_greenrope_identity_is_never_overwritten(self) -> None:
        store = FakeStore(identity())
        result = run_identity_binder(
            store=store,
            client=FakeClient(
                ["cefaeventid", "cefaformentryid"],
                opportunity(
                    current_event_id="different-event",
                    current_entry_id="9999",
                ),
            ),
            hmac_secret=SECRET,
            write_enabled=True,
        )

        self.assertEqual(1, result.conflicts)
        self.assertEqual(
            "greenrope_identity_conflict",
            store.states[0]["bridge_status"],
        )


if __name__ == "__main__":
    unittest.main()
