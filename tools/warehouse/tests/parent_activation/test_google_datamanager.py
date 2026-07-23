from __future__ import annotations

import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone

from parent_activation.config import ConsentState, GoogleConversionActionType
from parent_activation.google_datamanager import (
    GOOGLE_ADS_ACCOUNT_ID,
    INGEST_EVENTS_URL,
    GoogleDestination,
    GoogleMatchKeys,
    build_google_event,
    build_ingest_events_request,
    retrieve_request_status,
    send_ingest_events,
)


class GoogleDataManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.event_at = datetime(2026, 7, 23, 12, 34, 56, tzinfo=timezone.utc)
        self.outbox = {
            "event_timestamp": self.event_at.isoformat(),
            "transaction_id": "a" * 64,
        }
        self.keys = GoogleMatchKeys(
            gclid="real-gclid",
            click_id_captured_at=self.event_at - timedelta(days=2),
            email_transient=" Parent@Example.COM ",
            phone_transient="+1 (604) 555-0100",
            user_data_captured_at=self.event_at - timedelta(days=2),
            consent_state=ConsentState.GRANTED,
        )

    def test_build_request_uses_bare_upload_clicks_action_and_hashes_transient_data(self) -> None:
        event = build_google_event(self.outbox, self.keys)
        request = build_ingest_events_request(
            [event],
            GoogleDestination(conversion_action_id="123"),
            validate_only=True,
            consent_state=ConsentState.GRANTED,
        )

        self.assertEqual(
            GOOGLE_ADS_ACCOUNT_ID,
            request["destinations"][0]["operatingAccount"]["accountId"],
        )
        self.assertEqual("123", request["destinations"][0]["productDestinationId"])
        self.assertEqual({"adUserData": "CONSENT_GRANTED"}, request["consent"])
        self.assertTrue(request["validateOnly"])
        self.assertEqual("real-gclid", request["events"][0]["adIdentifiers"]["gclid"])
        identifiers = request["events"][0]["userData"]["userIdentifiers"]
        self.assertIn(
            {"emailAddress": hashlib.sha256(b"parent@example.com").hexdigest()},
            identifiers,
        )
        self.assertIn(
            {"phoneNumber": hashlib.sha256(b"+16045550100").hexdigest()},
            identifiers,
        )
        rendered = json.dumps(request)
        self.assertNotIn("Parent@Example.COM", rendered)
        self.assertNotIn("604) 555", rendered)

    def test_destination_rejects_resource_paths_and_non_upload_clicks_types(self) -> None:
        with self.assertRaisesRegex(ValueError, "bare numeric"):
            GoogleDestination(
                conversion_action_id="customers/4159217891/conversionActions/123"
            )
        with self.assertRaisesRegex(ValueError, "UPLOAD_CLICKS"):
            GoogleDestination(
                conversion_action_id="123",
                conversion_action_type="UPLOAD_CALLS",  # type: ignore[arg-type]
            )
        self.assertEqual(
            GoogleConversionActionType.UPLOAD_CLICKS,
            GoogleDestination("123").conversion_action_type,
        )

    def test_consent_fails_closed_for_click_and_user_matching(self) -> None:
        for state in (ConsentState.UNKNOWN, ConsentState.DENIED):
            keys = GoogleMatchKeys(
                gclid="real-gclid",
                click_id_captured_at=self.event_at,
                consent_state=state,
            )
            with self.assertRaisesRegex(ValueError, "explicitly granted"):
                build_google_event(self.outbox, keys)
            with self.assertRaisesRegex(ValueError, "explicitly granted"):
                build_ingest_events_request(
                    [{"eventTimestamp": self.event_at.isoformat()}],
                    GoogleDestination("123"),
                    consent_state=state,
                )

    def test_prehashed_values_are_validated_and_not_double_hashed(self) -> None:
        email_hash = hashlib.sha256(b"parent@example.com").hexdigest()
        phone_hash = hashlib.sha256(b"+16045550100").hexdigest()
        event = build_google_event(
            self.outbox,
            GoogleMatchKeys(
                email_sha256=email_hash,
                phone_sha256=phone_hash,
                user_data_captured_at=self.event_at,
                consent_state=ConsentState.GRANTED,
            ),
        )
        identifiers = event["userData"]["userIdentifiers"]
        self.assertIn({"emailAddress": email_hash}, identifiers)
        self.assertIn({"phoneNumber": phone_hash}, identifiers)
        with self.assertRaisesRegex(ValueError, "64-character"):
            build_google_event(
                self.outbox,
                GoogleMatchKeys(
                    email_sha256="parent@example.com",
                    user_data_captured_at=self.event_at,
                    consent_state=ConsentState.GRANTED,
                ),
            )

    def test_expired_identifiers_are_blocked_at_dispatch_boundary(self) -> None:
        with self.assertRaisesRegex(ValueError, "click identifier"):
            build_google_event(
                self.outbox,
                GoogleMatchKeys(
                    gclid="real-gclid",
                    click_id_captured_at=self.event_at - timedelta(days=90, seconds=1),
                    consent_state=ConsentState.GRANTED,
                ),
            )
        with self.assertRaisesRegex(ValueError, "enhanced lead"):
            build_google_event(
                self.outbox,
                GoogleMatchKeys(
                    email_sha256="b" * 64,
                    user_data_captured_at=self.event_at - timedelta(days=63, seconds=1),
                    consent_state=ConsentState.GRANTED,
                ),
            )

    def test_validate_only_defaults_true_and_diagnostics_normalize_without_network(self) -> None:
        captured: list[tuple[str, str, dict[str, str], object]] = []

        def transport(
            method: str,
            url: str,
            headers: dict[str, str],
            payload: object,
        ) -> dict[str, object]:
            captured.append((method, url, headers, payload))
            if method == "POST":
                return {"requestId": "request-123"}
            return {
                "requestStatusPerDestination": [
                    {
                        "requestStatus": "PARTIAL_SUCCESS",
                        "eventsIngestionStatus": {"recordCount": "2"},
                        "errorInfo": {
                            "errorCounts": [
                                {"reason": "PROCESSING_ERROR_REASON_EVENT_TOO_OLD"}
                            ]
                        },
                    }
                ]
            }

        event = build_google_event(self.outbox, self.keys)
        request = build_ingest_events_request(
            [event],
            GoogleDestination("123"),
            consent_state=ConsentState.GRANTED,
        )
        result = send_ingest_events(request, access_token="token", transport=transport)
        diagnostics = retrieve_request_status(
            "request-123",
            access_token="token",
            transport=transport,
        )

        self.assertTrue(result.validate_only)
        self.assertEqual("POST", captured[0][0])
        self.assertEqual(INGEST_EVENTS_URL, captured[0][1])
        self.assertEqual("GET", captured[1][0])
        self.assertEqual("partial_failure", diagnostics[0].normalized_status)
        self.assertTrue(diagnostics[0].terminal)
        self.assertEqual(2, diagnostics[0].record_count)


if __name__ == "__main__":
    unittest.main()
