from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "parent_activation" / "meta_capi.py"
SPEC = importlib.util.spec_from_file_location("meta_capi", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class MetaCapiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc)
        self.outbox = {
            "canonical_stage": "tour_scheduled",
            "event_timestamp": "2026-07-23T11:30:00Z",
            "platform_transaction_id": "hmac-parent-tour-scheduled",
            "school_uuid": "school-uuid-1",
        }

    def test_build_event_uses_crm_contract_and_hashes_pii(self) -> None:
        event = MODULE.build_meta_event(
            self.outbox,
            MODULE.MetaMatchKeys(
                email=" Parent@Example.COM ",
                phone="+1 (604) 555-0100",
                external_id="hmac-parent-identity",
                fbc="fb.1.123.real",
                fbp="fb.1.456.real",
                user_data_allowed=True,
            ),
            now=self.now,
        )

        self.assertEqual("CEFA_CRM_TourScheduled", event["event_name"])
        self.assertEqual("hmac-parent-tour-scheduled", event["event_id"])
        self.assertEqual("system_generated", event["action_source"])
        self.assertEqual("tour_scheduled", event["custom_data"]["cefa_canonical_stage"])
        self.assertEqual("school-uuid-1", event["custom_data"]["school_uuid"])
        self.assertEqual(["hmac-parent-identity"], event["user_data"]["external_id"])
        self.assertEqual([hashlib.sha256(b"parent@example.com").hexdigest()], event["user_data"]["em"])
        self.assertEqual([hashlib.sha256(b"16045550100").hexdigest()], event["user_data"]["ph"])
        self.assertEqual("fb.1.123.real", event["user_data"]["fbc"])
        self.assertEqual("fb.1.456.real", event["user_data"]["fbp"])
        rendered = json.dumps(event)
        self.assertNotIn("Parent@Example.COM", rendered)
        self.assertNotIn("604) 555", rendered)

    def test_empty_cookies_are_omitted_and_event_window_is_enforced(self) -> None:
        event = MODULE.build_meta_event(
            self.outbox,
            MODULE.MetaMatchKeys(external_id="hmac-parent-identity", fbc=" ", fbp=None),
            now=self.now,
        )
        self.assertNotIn("fbc", event["user_data"])
        self.assertNotIn("fbp", event["user_data"])
        old_outbox = dict(self.outbox)
        old_outbox["event_timestamp"] = (self.now - timedelta(days=7, seconds=1)).isoformat()
        with self.assertRaisesRegex(ValueError, "seven-day"):
            MODULE.build_meta_event(old_outbox, MODULE.MetaMatchKeys(external_id="hmac-parent-identity"), now=self.now)

    def test_send_uses_dataset_test_code_and_rejects_inquiry_submit(self) -> None:
        captured: list[tuple[str, str, dict[str, str], object]] = []

        def transport(method: str, url: str, headers: dict[str, str], payload: object) -> dict[str, object]:
            captured.append((method, url, headers, payload))
            return {"events_received": 1, "fbtrace_id": "trace-123", "messages": []}

        event = MODULE.build_meta_event(
            self.outbox, MODULE.MetaMatchKeys(external_id="hmac-parent-identity"), now=self.now
        )
        result = MODULE.send_meta_events(
            [event], access_token="token", test_event_code="TEST123", transport=transport
        )
        self.assertEqual(1, result.events_received)
        self.assertEqual("trace-123", result.trace_id)
        self.assertIn(f"/{MODULE.META_DATASET_ID}/events", captured[0][1])
        self.assertEqual("TEST123", captured[0][3]["test_event_code"])
        with self.assertRaisesRegex(ValueError, "approved CEFA CRM events"):
            MODULE.send_meta_events(
                [{"event_name": "Inquiry Submit"}], access_token="token", transport=transport
            )


if __name__ == "__main__":
    unittest.main()
