# Franchise USA Phase 1 Tracking Plan

Last updated: 2026-07-09

Governance note: Current owner is [Conversion tracking](../10-conversion-tracking/README.md). Update new franchise USA tracking summaries or final tracking decisions there. Status: `Current phase evidence`.

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
- GTM Version `25` is live as `2026-07-09 - Franchise USA stale in-house marker clearing`.
- Version `23` added one Google Ads tag for existing action `7482298930` on the confirmed Form `1` dispatch. Version `24` added the action's existing `600 CAD` value after no-send QA showed GTM otherwise transmitted value `0`. Version `25` limits the in-house marker to the active seven-day click window and clears stale in-house state on exact Reshift campaign/ad-set evidence without storing a partner marker.
- Legacy USA final conversion tags from the old Elementor/form-submit path were paused to avoid duplicate final conversions.
- Legacy active GA4, Google Ads, and Meta email/phone/application-click tags are now paused so the live USA container is closer to the agreed helper-event launch state.
- GA4 property `519783092` now has event-scoped custom dimensions registered for the low-cardinality helper payload fields.
- Form `2` has browser-resource evidence of a GA4 `generate_lead` hit to `G-YL1KQPWV0M` with helper metadata and matching event ID.
- GA4 property `519783092` reported processed USA `generate_lead` activity in the 2026-06-09 through 2026-07-08 audit window.
- Active USA campaign `23533022812` still optimizes to existing primary action `7482298930` / `Application Submit (USA)`. GTM tag `275` now sends that exact action only on confirmed Form `1` inquiry dispatch, with `event_id` as transaction ID, `600 CAD`, and enhanced conversions disabled. Legacy tag `218` remains paused.
- The old shared Meta pixel `918227085392601` was removed from the USA WordPress Insert Headers and Footers options after GTM Version `16` was published.
- Meta custom conversion `1915200622465036` / `USA Franchise Lead` was created on 2026-05-04 for dataset `1531247935333023`, using standard Meta `Lead` plus the `/inquiry-thank-you/` success path.
- Meta custom conversions `36521415357505819` / `CEFA | Franchise USA | In-House Lead` and `1352507926817889` / `CEFA | Franchise USA | Partner Lead` were created on 2026-07-01. The in-house conversion is live and proven. The partner campaign intentionally remains on broad conversion `1915200622465036` / `USA Franchise Lead` and is separated by campaign/ad-set ID. Version `25` now clears stale in-house state on exact partner campaign `120244631021580488`, ad set `120244631021560488`, or governed slug `reshift_meta`; it does not store a partner marker.
- USA Form `1` and Form `2` now populate Gravity Forms hidden attribution fields `14-30` in the browser from GAConnector cookies and URL parameters through GTM tag `270` / trigger `269`.

## Current Boundary

Active:
- USA GA4 helper-event mapping to `G-YL1KQPWV0M`.
- USA Meta base pixel dataset `1531247935333023` through `GTM-5LZMHBZL`.
- USA Meta standard `Lead` tags for Form `1` and Form `2` dispatch events with non-PII helper parameters and `eventID` from the helper payload.
- USA agency-test custom conversions exist in Meta, and GTM Version `25` publishes the in-house `cefa_agency_test` event parameter to the USA Meta `Lead` tags.
- Google Ads tag `275` publishes the existing `Application Submit (USA)` action only on Form `1` inquiry dispatch.
- Required infrastructure tags: Conversion Linker, Google/GA4 base tags, Google Ads remarketing, and GAConnector.
- Non-PII helper payload fields only.
- Hostname/context filters for `franchisecefa.com` and `www.franchisecefa.com`.
- Browser/dataLayer source for both current live forms.
- Browser-side hidden-field attribution writer for Form `1` and Form `2` fields `14-30`.
- Browser-level GA4 hit evidence for Form `2`.

Blocked / still needs signoff:
- Confirm delayed Google Ads platform receipt/status for controlled event `c1a582b5-642e-4db3-bf95-0a5e925db784`; the browser transport is proven, but the test had no served-ad click ID and should not be campaign-attributed.
- Continue the cross-property attribution bridge, CRM identity, warehouse, and automated-test work in the remediation blueprint.

Resolved audit interpretation:

- The apparent USA Meta browser `Lead` bursts came from unfiltered Pixel stats `aggregation=event` semantics, not 1,086 real inquiry events.
- Correct `aggregation=event_source&event=Lead` stats for 2026-07-01 through 2026-07-09 contain `7` browser and `6` server Lead events.
- Keep the working browser/CAPI tags and require event-filtered stats in future audits.

Do not map USA final events to the Canada shared Meta dataset by default. USA should remain more separated unless a live campaign dependency is explicitly confirmed.

## Files

- [GTM build and QA notes](./01-gtm-build-and-qa-2026-05-01.md)
- [QA and cutover checklist](./02-qa-and-cutover-checklist.md)
- [Post-Version-15 QA evidence, 2026-05-03](./03-post-version-15-qa-2026-05-03.md)
- [GTM Version 19 attribution field writer, 2026-05-06](./04-gtm-v19-attribution-field-writer-2026-05-06.md)
- [Agency-test Meta custom conversions, 2026-07-01](./05-agency-test-meta-custom-conversions-2026-07-01.md)
