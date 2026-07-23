from __future__ import annotations

import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone

from parent_activation.config import ConsentState
from parent_activation.meta_capi import (
    META_DATASET_ID,
    MetaMatchKeys,
    build_meta_event,
    send_meta_events,
)


class MetaCapiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc)
        self.outbox = {
            "canonical_stage": "tour_scheduled",
            "event_timestamp": "2026-07-23T11:30:00Z",
            "transaction_id": "a" * 64,
            "school_uuid": "school-uuid-1",
        }

    def test_build_event_uses_prehashed_match_keys_without_double_hashing(self) -> None:
        email_hash = hashlib.sha256(b"parent@example.com").hexdigest()
        phone_hash = hashlib.sha256(b"+16045550100").hexdigest()
        event = build_meta_event(
            self.outbox,
            MetaMatchKeys(
                email_sha256=email_hash,
                phone_sha256=phone_hash,
                external_id="b" * 64,
                fbc="fb.1.123.real",
                fbp="fb.1.456.real",
                consent_state=ConsentState.GRANTED,
            ),
            now=self.now,
        )

        self.assertEqual("CEFA_CRM_TourScheduled", event["event_name"])
        self.assertEqual("a" * 64, event["event_id"])
        self.assertEqual("system_generated", event["action_source"])
        self.assertEqual("tour_scheduled", event["custom_data"]["cefa_canonical_stage"])
        self.assertEqual("school-uuid-1", event["custom_data"]["school_uuid"])
        self.assertEqual(["b" * 64], event["user_data"]["external_id"])
        self.assertEqual([email_hash], event["user_data"]["em"])
        self.assertEqual([phone_hash], event["user_data"]["ph"])
        self.assertEqual("fb.1.123.real", event["user_data"]["fbc"])
        self.assertEqual("fb.1.456.real", event["user_data"]["fbp"])

    def test_transient_raw_values_use_shared_normalization_and_never_render_raw(self) -> None:
        event = build_meta_event(
            self.outbox,
            MetaMatchKeys(
                email_transient=" Parent@Example.COM ",
                phone_transient="(604) 555-0100",
                external_id="b" * 64,
                consent_state=ConsentState.GRANTED,
            ),
            now=self.now,
        )
        self.assertEqual(
            [hashlib.sha256(b"parent@example.com").hexdigest()],
            event["user_data"]["em"],
        )
        self.assertEqual(
            [hashlib.sha256(b"+16045550100").hexdigest()],
            event["user_data"]["ph"],
        )
        rendered = json.dumps(event)
        self.assertNotIn("Parent@Example.COM", rendered)
        self.assertNotIn("604) 555", rendered)

    def test_consent_fails_closed_and_external_id_is_not_a_real_match_key(self) -> None:
        for state in (ConsentState.UNKNOWN, ConsentState.DENIED):
            with self.assertRaisesRegex(ValueError, "explicitly granted"):
                build_meta_event(
                    self.outbox,
                    MetaMatchKeys(
                        external_id="b" * 64,
                        fbc="fb.1.123.real",
                        consent_state=state,
                    ),
                    now=self.now,
                )
        with self.assertRaisesRegex(ValueError, "real match key"):
            build_meta_event(
                self.outbox,
                MetaMatchKeys(
                    external_id="b" * 64,
                    consent_state=ConsentState.GRANTED,
                ),
                now=self.now,
            )

    def test_cookie_format_and_event_window_are_enforced(self) -> None:
        with self.assertRaisesRegex(ValueError, "captured-cookie"):
            build_meta_event(
                self.outbox,
                MetaMatchKeys(
                    external_id="b" * 64,
                    fbc="manufactured-cookie",
                    consent_state=ConsentState.GRANTED,
                ),
                now=self.now,
            )
        old_outbox = dict(self.outbox)
        old_outbox["event_timestamp"] = (
            self.now - timedelta(days=7, seconds=1)
        ).isoformat()
        with self.assertRaisesRegex(ValueError, "seven-day"):
            build_meta_event(
                old_outbox,
                MetaMatchKeys(
                    external_id="b" * 64,
                    fbc="fb.1.123.real",
                    consent_state=ConsentState.GRANTED,
                ),
                now=self.now,
            )

    def test_send_uses_dataset_test_code_and_rejects_inquiry_submit(self) -> None:
        captured: list[tuple[str, str, dict[str, str], object]] = []

        def transport(
            method: str,
            url: str,
            headers: dict[str, str],
            payload: object,
        ) -> dict[str, object]:
            captured.append((method, url, headers, payload))
            return {"events_received": 1, "fbtrace_id": "trace-123", "messages": []}

        event = build_meta_event(
            self.outbox,
            MetaMatchKeys(
                external_id="b" * 64,
                fbc="fb.1.123.real",
                consent_state=ConsentState.GRANTED,
            ),
            now=self.now,
        )
        result = send_meta_events(
            [event],
            access_token="token",
            test_event_code="TEST123",
            transport=transport,
        )
        self.assertEqual(1, result.events_received)
        self.assertEqual("trace-123", result.trace_id)
        self.assertIn(f"/{META_DATASET_ID}/events", captured[0][1])
        self.assertEqual("TEST123", captured[0][3]["test_event_code"])
        with self.assertRaisesRegex(ValueError, "approved CEFA CRM events"):
            send_meta_events(
                [{"event_name": "Inquiry Submit"}],
                access_token="token",
                transport=transport,
            )


if __name__ == "__main__":
    unittest.main()
