# Changelog

## Unreleased

- Added the live-domain status note for the parent cutover and franchise WPCode bridge rollout.
- Added `snippets/franchise-wpcode-bridge.php` as a temporary live franchise deployment fallback for hosts where normal plugin-file writes are blocked.
- Updated the franchise bridge to fetch one-time thank-you payloads with `POST` plus `cache: no-store` to avoid cached GET payload reuse.
- Verified live Franchise Canada Form `1` and Form `2` confirmed-success dataLayer events through the WPCode bridge.
- Verified live Franchise USA Form `1` and Form `2` confirmed-success dataLayer events through the WPCode bridge.
- Published USA GTM Version `15` with hostname/context-scoped helper-event GA4 mapping for Franchise USA Forms `1` and `2`.
- Paused old USA final conversion tags from legacy Elementor/form-submit paths while keeping USA Ads/Meta final helper-event mapping blocked until platform IDs are confirmed.
- Added Franchise USA Phase 1 GTM build notes and QA checklist.
- Added Franchise USA hostname support for Form 1 `franchise_inquiry_submit` and Form 2 `real_estate_site_submit` with `site_context=franchise_us`, `market=usa`, and `country=US`.
- Stopped the browser bridge from overwriting Form 4 School Manager business subfields `32.3` and `32.7`; the plugin now derives days/program metadata for tracking without changing submitted lead values.
- Normalized legacy pipe-delimited `days_per_week` values only in the dataLayer payload so historical entries can still report cleanly without mutating Gravity Forms entries or KinderTales delivery.
- Added hostname-scoped configuration for parent and Franchise Canada tracking contracts.
- Added Franchise Canada Form 1 `franchise_inquiry_submit` and Form 2 `real_estate_site_submit` confirmed-success payloads.
- Added Gravity Forms entry-meta event ID storage for supported forms without a dedicated event ID field.
- Kept Franchise Canada GAConnector fields `14` through `30` as read-only attribution inputs for now.
- Added parent production cutover checklist with the current GA4 custom-dimension and key-event state.
- Added cross-property measurement boundary notes for parent, franchise Canada, and franchise USA.
- Documented franchise Canada subdomain GTM containment risk and Meta dataset separation recommendation.
- Added GPT Pro review handoff covering parent implementation state, franchise rollout, and Meta learning-loss questions.
- Added GPT Pro franchise transition final pack and reviewed plan adopting the phased Canada Meta transition, USA separation default, GTM containment, and CAPI/sGTM sequencing.

## 0.3.0 - 2026-04-27

- Ported the old parent-site attribution-cookie pattern into the CEFA-owned tracking bridge.
- Added 90-day first-party cookies and localStorage mirrors for first landing page, first referrer, last UTM values, and click IDs.
- Added browser writeback for Form 4 attribution fields `35` through `46`.
- Added server-side `gform_pre_submission_4` fallback writeback from cookies for the same attribution fields.
- Added attribution fields to the confirmed `school_inquiry_submit` dataLayer payload.

## 0.2.7 - 2026-04-26

- Increased Form 4 diagnostic micro-event delays so GTM receives helper-plugin form events after Gravity Forms validation and automatic form measurement handlers settle.

## 0.2.6 - 2026-04-26

- Synced Form 4 tracking-only Field 32 hidden values for selected program name and days per week before dataLayer reads and submission.

## 0.2.5 - 2026-04-26

- Delayed Form 4 micro-event pushes slightly so structured helper-plugin events fire after Gravity Forms and browser form-measurement handlers settle.

## 0.2.4 - 2026-04-26

- Fixed validation-error tracking for Gravity Forms layouts where the validation summary renders outside the `<form>` while invalid fields remain inside Form 4.

## 0.2.3 - 2026-04-26

- Made Form 4 tracking attach to all duplicate Gravity Forms instances rendered on the page.
- Fixed validation-error tracking to read from the form instance that actually contains Gravity Forms validation messages.

## 0.2.2 - 2026-04-26

- Added submit-button click tracking so Gravity Forms iframe/AJAX submissions emit `form_submit_click`.
- Added Gravity Forms rerender and mutation handling so validation messages emit `validation_error`.

## 0.2.1 - 2026-04-26

- Normalized micro-conversion payloads so every GTM-mapped key is explicitly reset per event.
- Prevented stale dataLayer metadata from carrying from one micro event into the next GA4 hit.

## 0.2.0 - 2026-04-25

- Added plugin-owned Phase 1A micro-conversion dataLayer events.
- Added `parent_inquiry_cta_click`, `find_a_school_click`, `phone_click`, `email_click`, `form_start`, `form_submit_click`, and `validation_error`.
- Added structured metadata for page context, CTA context, Form 4 context, school/program/day values, and micro-event IDs.
- Added a short navigation delay for tracked same-window CTA/link clicks so GTM has time to process the plugin dataLayer event before navigation.
- Kept the confirmed `school_inquiry_submit` contract unchanged.

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
