# Changelog

## 0.1.6 - 2026-04-24

- Scoped browser event ID reads to the submitted Form 4 instance to avoid duplicate Gravity Forms markup using the wrong hidden field.
- Added Gravity Forms AJAX iframe confirmation handling so the confirmed payload can be fetched when the submission succeeds without a full page redirect.

## 0.1.5 - 2026-04-24

- Release bump for staging replacement after confirming staging was still running the old `0.1.2` PHP build.
- Keeps the `0.1.4` behavior: no inline form-page success push; final event should come from the thank-you payload flow only.

## 0.1.4 - 2026-04-24

- Removed the inline form-page success push so the final event is emitted from the thank-you page payload flow only.
- Keeps the helper plugin from creating a pre-redirect duplicate when Gravity Forms returns an intermediate confirmation response.

## 0.1.3 - 2026-04-24

- Added a server-confirmed event ID payload fallback for thank-you flows where another plugin rewrites the confirmation query string.
- Stored payloads after successful Form 4 submission so the browser can retrieve them by the saved `32.4` event ID.
- Removed the plugin homepage header so WordPress does not show a "Visit plugin site" link.

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
