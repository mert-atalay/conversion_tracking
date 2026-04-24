# Changelog

## 0.1.2 - 2026-04-24

- Moved the Gravity Forms confirmation hook to a late priority so the tracking token is appended after School Manager confirmation query parameters.

## 0.1.1 - 2026-04-24

- Added support for Gravity Forms page confirmations by appending the one-time tracking token to the page confirmation query string.

## 0.1.0 - 2026-04-24

- Initial CEFA Phase 1A tracking bridge.
- Added Form 4 event ID guarantee for field `32.4`.
- Added tokenized successful-submission payload for thank-you page tracking.
- Added one-time `school_inquiry_submit` `dataLayer` event push.
- Added direct thank-you, reload, and duplicate-source guardrails.
