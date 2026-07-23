from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from parent_activation.normalization import (
    google_click_id_is_eligible,
    google_user_data_is_eligible,
    hmac_platform_event_id,
    meta_event_is_eligible,
    normalize_email,
    normalize_phone,
    sha256_normalized_email,
    sha256_normalized_phone,
)


class NormalizationTests(unittest.TestCase):
    def test_email_and_phone_are_normalized_before_hashing(self) -> None:
        self.assertEqual("parent@example.com", normalize_email(" Parent@Example.COM "))
        self.assertEqual("+16045551212", normalize_phone("(604) 555-1212"))
        self.assertEqual(64, len(sha256_normalized_email(" Parent@Example.COM ") or ""))
        self.assertEqual(
            sha256_normalized_phone("+1 604 555 1212"),
            sha256_normalized_phone("(604) 555-1212"),
        )

    def test_hmac_is_stable_and_secret_scoped(self) -> None:
        first = hmac_platform_event_id("secret-a", "4159217891", "form4_event", "evt-1", "tour_scheduled")
        second = hmac_platform_event_id("secret-a", "4159217891", "form4_event", "evt-1", "tour_scheduled")
        changed = hmac_platform_event_id("secret-b", "4159217891", "form4_event", "evt-1", "tour_scheduled")
        repeated = hmac_platform_event_id(
            "secret-a", "4159217891", "form4_event", "evt-1", "tour_scheduled", 2
        )
        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)
        self.assertNotEqual(first, repeated)
        self.assertEqual(64, len(first))

    def test_platform_age_windows_are_strict(self) -> None:
        now = datetime(2026, 7, 23, tzinfo=timezone.utc)
        self.assertTrue(google_click_id_is_eligible(now - timedelta(days=90), now))
        self.assertFalse(google_click_id_is_eligible(now - timedelta(days=90, seconds=1), now))
        self.assertTrue(google_user_data_is_eligible(now - timedelta(days=63), now))
        self.assertFalse(google_user_data_is_eligible(now - timedelta(days=64), now))
        self.assertTrue(meta_event_is_eligible(now - timedelta(days=7), now))
        self.assertFalse(meta_event_is_eligible(now - timedelta(days=7, seconds=1), now))


if __name__ == "__main__":
    unittest.main()
