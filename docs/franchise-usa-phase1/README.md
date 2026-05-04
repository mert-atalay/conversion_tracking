# Franchise USA Phase 1 Tracking Plan

Last updated: 2026-05-04

This folder is the working implementation package for Franchise USA tracking.

Scope:
- Current/live USA franchise property: `https://franchisecefa.com` and `https://www.franchisecefa.com`
- Former USA staging property: `https://cefafranusdev.wpenginepowered.com`
- GTM account: `6004334435`
- USA franchise GTM container: `GTM-5LZMHBZL` / container `204988779`
- GA4 property: `519783092` / `CEFA Franchise - USA.`
- Linked Google Ads customers: `3820636025`, `4159217891`
- Primary website forms:
  - Gravity Forms Form `1` / Franchise Inquiry
  - Gravity Forms Form `2` / Submit a Site

## Current State

- The live USA site renders the WPCode fallback bridge from `snippets/franchise-wpcode-bridge.php`.
- Current production form URLs are:
  - Form `1`: `https://franchisecefa.com/available-opportunities/franchising-inquiry/`
  - Form `2`: `https://franchisecefa.com/partner-with-cefa/real-estate-partners/submit-a-site/`
- Older test paths `/franchise-application/` and `/real-estate-submission/` now return `404`; do not use them for launch QA.
- Controlled submissions after GTM Version `15` proved the website-side confirmed-success dataLayer events:
  - Form `1`: `franchise_inquiry_submit`
  - Form `2`: `real_estate_site_submit`
- The helper payload uses `site_context=franchise_us`, `market=usa`, and `country=US`.
- GTM Version `18` is live as `CEFA Franchise USA Meta Lead reliability fix - 2026-05-04`.
- GTM Version `18` keeps the Version `15` helper-event and GA4 mapping, keeps the Version `16` USA Meta dataset split to `1531247935333023`, keeps the Version `17` legacy micro/click cleanup, and adds a Meta `fbq` init fallback on the two USA `Lead` tags.
- Legacy USA final conversion tags from the old Elementor/form-submit path were paused to avoid duplicate final conversions.
- Legacy active GA4, Google Ads, and Meta email/phone/application-click tags are now paused so the live USA container is closer to the agreed helper-event launch state.
- GA4 property `519783092` now has event-scoped custom dimensions registered for the low-cardinality helper payload fields.
- Form `2` has browser-resource evidence of a GA4 `generate_lead` hit to `G-YL1KQPWV0M` with helper metadata and matching event ID.
- GA4 Data API and realtime checks on 2026-05-03 did not yet show processed USA `generate_lead` rows, so report processing confirmation remains open.
- GA4 property `519783092` is linked to Google Ads customers `3820636025` and `4159217891`; USA-related imported conversion actions exist in both accounts, but the observed USA actions still had zero all-conversion volume in the 2025-05-01 to 2026-05-03 reporting query.
- The old shared Meta pixel `918227085392601` was removed from the USA WordPress Insert Headers and Footers options after GTM Version `16` was published.
- Meta custom conversion `1915200622465036` / `USA Franchise Lead` was created on 2026-05-04 for dataset `1531247935333023`, using standard Meta `Lead` plus the `/inquiry-thank-you/` success path.

## Current Boundary

Active:
- USA GA4 helper-event mapping to `G-YL1KQPWV0M`.
- USA Meta base pixel dataset `1531247935333023` through `GTM-5LZMHBZL`.
- USA Meta standard `Lead` tags for Form `1` and Form `2` dispatch events with non-PII helper parameters and `eventID` from the helper payload.
- Required infrastructure tags: Conversion Linker, Google/GA4 base tags, Google Ads remarketing, and GAConnector.
- Non-PII helper payload fields only.
- Hostname/context filters for `franchisecefa.com` and `www.franchisecefa.com`.
- Browser/dataLayer source for both current live forms.
- Browser-level GA4 hit evidence for Form `2`.

Blocked / still needs signoff:
- USA Google Ads final helper-event tags until the correct account and conversion action are confirmed for optimization.
- Meta Events Manager receipt confirmation for dataset `1531247935333023`; the USA custom conversion now exists, but Events Manager still needs to show live `Lead` receipt before optimization signoff.
- Final USA GA4 reporting signoff until processed reports show the post-Version-15 controlled submissions and the property currency setting is confirmed.

Do not map USA final events to the Canada shared Meta dataset by default. USA should remain more separated unless a live campaign dependency is explicitly confirmed.

## Files

- [GTM build and QA notes](./01-gtm-build-and-qa-2026-05-01.md)
- [QA and cutover checklist](./02-qa-and-cutover-checklist.md)
- [Post-Version-15 QA evidence, 2026-05-03](./03-post-version-15-qa-2026-05-03.md)
