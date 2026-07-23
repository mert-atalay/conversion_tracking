from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[2] / "parent_activation" / "google_datamanager.py"
SPEC = importlib.util.spec_from_file_location("google_datamanager", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class GoogleDataManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.outbox = {
            "event_timestamp": "2026-07-23T12:34:56Z",
            "platform_transaction_id": "hmac-parent-tour-scheduled",
        }
        self.keys = MODULE.GoogleMatchKeys(
            gclid="real-gclid",
            email=" Parent@Example.COM ",
            phone="+1 (604) 555-0100",
            user_data_allowed=True,
        )

    def test_build_request_uses_configured_destination_and_hashes_user_data(self) -> None:
        event = MODULE.build_google_event(self.outbox, self.keys)
        request = MODULE.build_ingest_events_request(
            [event],
            MODULE.GoogleDestination(product_destination_id="customers/4159217891/conversionActions/123"),
            validate_only=True,
        )

        self.assertEqual("4159217891", request["destinations"][0]["operatingAccount"]["accountId"])
        self.assertEqual(
            "customers/4159217891/conversionActions/123",
            request["destinations"][0]["productDestinationId"],
        )
        self.assertTrue(request["validateOnly"])
        self.assertEqual("WEB", request["events"][0]["eventSource"])
        self.assertEqual("real-gclid", request["events"][0]["adIdentifiers"]["gclid"])
        identifiers = request["events"][0]["userData"]["userIdentifiers"]
        self.assertIn({"emailAddress": hashlib.sha256(b"parent@example.com").hexdigest()}, identifiers)
        self.assertIn({"phoneNumber": hashlib.sha256(b"16045550100").hexdigest()}, identifiers)
        rendered = json.dumps(request)
        self.assertNotIn("Parent@Example.COM", rendered)
        self.assertNotIn("604) 555", rendered)
        self.assertNotIn("consent", request)

    def test_real_ids_only_and_user_data_requires_explicit_permission(self) -> None:
        event = MODULE.build_google_event(
            self.outbox,
            MODULE.GoogleMatchKeys(gbraid="real-gbraid", email="parent@example.com"),
        )
        self.assertEqual({"gbraid": "real-gbraid"}, event["adIdentifiers"])
        self.assertNotIn("userData", event)
        with self.assertRaisesRegex(ValueError, "real click ID or approved user data"):
            MODULE.build_google_event(self.outbox, MODULE.GoogleMatchKeys(email="parent@example.com"))

    def test_validate_only_defaults_to_true(self) -> None:
        event = MODULE.build_google_event(self.outbox, MODULE.GoogleMatchKeys(gclid="real-gclid"))
        request = MODULE.build_ingest_events_request(
            [event], MODULE.GoogleDestination(product_destination_id="action-123")
        )
        self.assertTrue(request["validateOnly"])

    def test_send_and_normalize_diagnostics_without_network(self) -> None:
        captured: list[tuple[str, str, dict[str, str], object]] = []

        def transport(method: str, url: str, headers: dict[str, str], payload: object) -> dict[str, object]:
            captured.append((method, url, headers, payload))
            if method == "POST":
                return {"requestId": "request-123"}
            return {
                "requestStatusPerDestination": [
                    {
                        "requestStatus": "PARTIAL_SUCCESS",
                        "eventsIngestionStatus": {"recordCount": "2"},
                        "errorInfo": {"errorCounts": [{"reason": "PROCESSING_ERROR_REASON_EVENT_TOO_OLD"}]},
                    }
                ]
            }

        event = MODULE.build_google_event(self.outbox, self.keys)
        request = MODULE.build_ingest_events_request(
            [event], MODULE.GoogleDestination(product_destination_id="action-123"), validate_only=False
        )
        result = MODULE.send_ingest_events(request, access_token="token", transport=transport)
        diagnostics = MODULE.retrieve_request_status("request-123", access_token="token", transport=transport)

        self.assertEqual("request-123", result.request_id)
        self.assertFalse(result.validate_only)
        self.assertEqual("POST", captured[0][0])
        self.assertEqual(MODULE.INGEST_EVENTS_URL, captured[0][1])
        self.assertEqual("GET", captured[1][0])
        self.assertIn("requestId=request-123", captured[1][1])
        self.assertEqual("partial_failure", diagnostics[0].normalized_status)
        self.assertTrue(diagnostics[0].terminal)
        self.assertEqual(2, diagnostics[0].record_count)


if __name__ == "__main__":
    unittest.main()
