from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from parent_activation.greenrope_identity_writer import build_identity_edit_xml
from parent_activation.identity_bridge import (
    SchoolBinding,
    build_identity_record,
    parse_greenrope_candidate,
    select_identity_match,
)
from parent_activation.identity_http import process_webhook


SECRET = b"unit-test-secret"
SCHOOL_UUID = "81237895-bcad-11ef-8bcb-028d36469a89"
BINDINGS = {
    SCHOOL_UUID: SchoolBinding(
        school_uuid=SCHOOL_UUID,
        school_slug="surrey-campbell-heights",
        school_name="Surrey - Campbell Heights",
        greenrope_group_id="58",
    )
}
PAYLOAD = {
    "form_id": "4",
    "entry_id": "8017",
    "submitted_at": "2026-07-23T12:00:00Z",
    "event_id": "cefa-parent-event-8017",
    "school_uuid": SCHOOL_UUID,
    "parent_first": "Example",
    "parent_last": "Parent",
    "email": "parent@example.com",
    "phone": "+1 (604) 555-0100",
    "child_dob": "2023-03-04",
    "program": "Junior Kindergarten",
    "requested_start": "2026-09-01",
    "consent": "checked",
}


def raw_opportunity(
    *,
    opportunity_id: str = "greenrope-1",
    created_at: str = "2026-07-23 12:05:00",
    email: str = "parent@example.com",
    phone: str = "6045550100",
) -> dict[str, object]:
    return {
        "opportunity_id": opportunity_id,
        "createdate": created_at,
        "quality": "5",
        "closedate": "2026-12-31",
        "assignedtoemail": email,
        "assignedtomobile": phone,
        "assignedtofirstname": "Example",
        "assignedtolastname": "Parent",
        "customfields": {
            "customfield": [
                {"fieldname": "child_dob", "fieldvalue": "2023-03-04"},
                {
                    "fieldname": "program_name",
                    "fieldvalue": "Junior Kindergarten",
                },
                {
                    "fieldname": "requested_start_date",
                    "fieldvalue": "2026-09-01",
                },
            ]
        },
    }


class FakeStore:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def upsert_identity(self, record: dict[str, object]) -> None:
        self.rows.append(dict(record))


class IdentityBridgeTests(unittest.TestCase):
    def test_capture_persists_hmacs_and_no_raw_identity(self) -> None:
        record = build_identity_record(
            PAYLOAD,
            secret=SECRET,
            school_bindings=BINDINGS,
            received_at=datetime(2026, 7, 23, 12, 1, tzinfo=timezone.utc),
        )

        serialized = json.dumps(record, sort_keys=True)
        self.assertEqual("captured", record["bridge_status"])
        self.assertEqual("58", record["greenrope_group_id"])
        self.assertEqual(64, len(str(record["assigned_email_hmac"])))
        self.assertNotIn("parent@example.com", serialized)
        self.assertNotIn("6045550100", serialized)
        self.assertNotIn("Example", serialized)
        self.assertNotIn("2023-03-04", serialized)

    def test_match_requires_email_group_window_and_four_supporting_fields(self) -> None:
        identity = build_identity_record(
            PAYLOAD,
            secret=SECRET,
            school_bindings=BINDINGS,
            received_at=datetime(2026, 7, 23, 12, 1, tzinfo=timezone.utc),
        )
        candidate = parse_greenrope_candidate(
            raw_opportunity(),
            group_id="58",
            secret=SECRET,
        )

        decision = select_identity_match(identity, [candidate])

        self.assertEqual("matched", decision.status)
        self.assertIs(candidate, decision.candidate)
        self.assertEqual(6, decision.match_score)

    def test_match_quarantines_missing_and_ambiguous_candidates(self) -> None:
        identity = build_identity_record(
            PAYLOAD,
            secret=SECRET,
            school_bindings=BINDINGS,
            received_at=datetime(2026, 7, 23, 12, 1, tzinfo=timezone.utc),
        )
        late = parse_greenrope_candidate(
            raw_opportunity(
                opportunity_id="late",
                created_at=(
                    datetime(2026, 7, 23, 12, tzinfo=timezone.utc)
                    + timedelta(days=2)
                ).isoformat(),
            ),
            group_id="58",
            secret=SECRET,
        )
        self.assertEqual(
            "no_candidate",
            select_identity_match(identity, [late]).reason,
        )

        first = parse_greenrope_candidate(
            raw_opportunity(opportunity_id="first"),
            group_id="58",
            secret=SECRET,
        )
        second = parse_greenrope_candidate(
            raw_opportunity(opportunity_id="second"),
            group_id="58",
            secret=SECRET,
        )
        self.assertEqual(
            "ambiguous_candidate",
            select_identity_match(identity, [first, second]).reason,
        )

    def test_greenrope_edit_preserves_required_fields_and_escapes_values(self) -> None:
        candidate = parse_greenrope_candidate(
            raw_opportunity(opportunity_id='id-"unsafe'),
            group_id="58",
            secret=SECRET,
        )
        xml = build_identity_edit_xml(
            account_id="account-1",
            candidate=candidate,
            event_id="event-1",
            form_entry_id="8017",
        )

        self.assertIn("<Quality>5</Quality>", xml)
        self.assertIn("<CloseDate>20261231</CloseDate>", xml)
        self.assertIn('opportunity_id="id-&quot;unsafe"', xml)
        self.assertIn('fieldname="cefa_event_id"', xml)
        self.assertIn('fieldname="cefa_form_entry_id"', xml)

    def test_webhook_rejects_bad_secret_and_accepts_selected_payload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            school_map = Path(directory) / "map.csv"
            school_map.write_text(
                "contract_version,school_uuid,school_slug,school_name,"
                "greenrope_group_id,status\n"
                f"parent_crm_v1,{SCHOOL_UUID},surrey-campbell-heights,"
                "Surrey - Campbell Heights,58,enabled\n",
                encoding="utf-8",
            )
            store = FakeStore()
            unauthorized, _ = process_webhook(
                headers={"X-CEFA-Identity-Secret": "wrong"},
                body=json.dumps(PAYLOAD).encode(),
                webhook_secret="correct",
                identity_secret=SECRET,
                school_map_path=school_map,
                store=store,
            )
            accepted, _ = process_webhook(
                headers={"X-CEFA-Identity-Secret": "correct"},
                body=json.dumps(PAYLOAD).encode(),
                webhook_secret="correct",
                identity_secret=SECRET,
                school_map_path=school_map,
                store=store,
                received_at=datetime(2026, 7, 23, 12, 1, tzinfo=timezone.utc),
            )

        self.assertEqual(401, unauthorized)
        self.assertEqual(202, accepted)
        self.assertEqual(1, len(store.rows))


if __name__ == "__main__":
    unittest.main()
