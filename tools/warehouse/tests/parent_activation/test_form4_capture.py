from __future__ import annotations

from datetime import datetime, timezone
import json
import unittest

from parent_activation.form4_capture import capture_new_form4_identities
from parent_activation.identity_bridge import SchoolBinding


SECRET = b"unit-test-secret"
SCHOOL_UUID = "81237895-bcad-11ef-8bcb-028d36469a89"


class FakeClient:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows
        self.calls: list[tuple[int, int]] = []

    def entries(self, *, page: int, page_size: int) -> list[dict[str, object]]:
        self.calls.append((page, page_size))
        return self.rows if page == 1 else []


class FakeStore:
    def __init__(self, latest: datetime | None = None) -> None:
        self.latest = latest
        self.rows: list[dict[str, object]] = []

    def latest_submitted_at(self) -> datetime | None:
        return self.latest

    def upsert_identity(self, record: dict[str, object]) -> None:
        self.rows.append(dict(record))


def entry(
    entry_id: str,
    submitted_at: str,
    *,
    event_id: str = "cefa-parent-event",
) -> dict[str, object]:
    return {
        "form_id": "4",
        "id": entry_id,
        "date_created": submitted_at,
        "32.4": f"{event_id}-{entry_id}",
        "32.1": SCHOOL_UUID,
        "32.5": "surrey-campbell-heights",
        "32.6": "Surrey - Campbell Heights",
        "4.3": "Example",
        "5.6": "Parent",
        "6": "parent@example.com",
        "7": "6045550100",
        "26": "2023-03-04",
        "32.7": "Junior Kindergarten",
        "49": "2026-09-01",
    }


class Form4CaptureTests(unittest.TestCase):
    def test_only_prospective_entries_are_hmaced_and_upserted(self) -> None:
        client = FakeClient(
            [
                entry("2", "2026-07-23T21:05:00Z"),
                entry("1", "2026-07-23T20:55:00Z"),
                entry("0", "2026-07-23T19:00:00Z"),
            ]
        )
        store = FakeStore()
        result = capture_new_form4_identities(
            client=client,
            store=store,
            identity_secret=SECRET,
            school_bindings={
                SCHOOL_UUID: SchoolBinding(
                    SCHOOL_UUID,
                    "surrey-campbell-heights",
                    "Surrey - Campbell Heights",
                    "58",
                )
            },
            activation_start=datetime(
                2026,
                7,
                23,
                20,
                30,
                tzinfo=timezone.utc,
            ),
            observed_at=datetime(
                2026,
                7,
                23,
                21,
                10,
                tzinfo=timezone.utc,
            ),
            page_size=100,
        )

        self.assertEqual(2, result.entries_observed)
        self.assertEqual(2, result.identities_upserted)
        self.assertEqual(2, len(store.rows))
        serialized = json.dumps(store.rows)
        self.assertNotIn("parent@example.com", serialized)
        self.assertNotIn("6045550100", serialized)
        self.assertNotIn("Example", serialized)

    def test_overlap_is_idempotent_and_invalid_rows_are_aggregate_only(self) -> None:
        rows = [
            entry("3", "2026-07-23T21:05:00Z"),
            entry("3", "2026-07-23T21:05:00Z"),
            entry("4", "invalid"),
        ]
        store = FakeStore(
            datetime(2026, 7, 23, 21, 0, tzinfo=timezone.utc)
        )
        result = capture_new_form4_identities(
            client=FakeClient(rows),
            store=store,
            identity_secret=SECRET,
            school_bindings={
                SCHOOL_UUID: SchoolBinding(
                    SCHOOL_UUID,
                    "surrey-campbell-heights",
                    "Surrey - Campbell Heights",
                    "58",
                )
            },
            activation_start=datetime(
                2026,
                7,
                23,
                20,
                tzinfo=timezone.utc,
            ),
            observed_at=datetime(
                2026,
                7,
                23,
                21,
                10,
                tzinfo=timezone.utc,
            ),
        )

        self.assertEqual(1, result.identities_upserted)
        self.assertEqual(1, result.invalid_entries)


if __name__ == "__main__":
    unittest.main()
