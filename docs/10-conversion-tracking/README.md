# Conversion Tracking Workstream

This folder is the routing surface for CEFA conversion tracking across:

- Parent `cefa.ca`
- Franchise Canada `franchise.cefa.ca`
- Franchise USA `www.franchisecefa.com`
- GTM, GA4, Google Ads, Meta, CAPI, Measurement Protocol, and sGTM

## Current Canonical Files

- [Plugin README](../../README.md)
- [Live conversion tracking status](../live-conversion-tracking-status-2026-05-01.md)
- [Parent production cutover checklist](../parent-production-cutover-checklist.md)
- [Cross-property measurement boundaries](../cross-property-measurement-boundaries.md)
- [Phase 1A docs](../phase1a/README.md)
- [Phase 1B Measurement Protocol/server-side options](../phase1b-measurement-protocol-server-side-options-2026-05-01.md)
- [Franchise Canada Phase 1 docs](../franchise-canada-phase1/README.md)
- [Franchise USA Phase 1 docs](../franchise-usa-phase1/README.md)
- [Franchise CA/USA tracking status, 2026-05-03](./franchise-ca-usa-tracking-status-2026-05-03.md)
- [Franchise transition final pack](../franchise-transition-final-pack-v1/00-executive-summary-and-final-decision.md)
- [Business truth and tracking data gaps, 2026-05-03](./business-truth-and-tracking-data-gaps-2026-05-03.md)
- [Parent current state and remaining work, 2026-05-04](./parent-current-state-and-remaining-work-2026-05-04.md)
- [Google platform access status, 2026-05-04](./google-platform-access-status-2026-05-04.md)
- [Current access implementation plan, 2026-05-04](./current-access-implementation-plan-2026-05-04.md)
- [Parent Google / GTM / Ads signoff, 2026-05-04](./parent-google-gtm-ads-signoff-2026-05-04.md)
- [WP Engine WP-CLI access POC, 2026-05-04](./wpengine-wpcli-access-poc-2026-05-04.md)
- [Live conversion tracking recheck, 2026-05-04](./live-conversion-tracking-recheck-2026-05-04.md)
- [Live main conversion event audit, 2026-05-04](./live-main-conversion-event-audit-2026-05-04.md)
- [Ad launch readiness test, 2026-05-04](./ad-launch-readiness-test-2026-05-04.md)
- [Event ownership matrix, 2026-05-05](./event-ownership-matrix-2026-05-05.md)
- [Franchise Canada post-v54 application-submit QA, 2026-05-05](../franchise-canada-phase1/08-post-v54-application-submit-qa-2026-05-05.md)
- [Event taxonomy Google Sheet working copy](https://docs.google.com/spreadsheets/d/1ztfakcO0oDbO2WVeKCAGOa7c9ks9EHuflfLvVOEiadU/edit)

## Current Rules

- Parent final website event: `school_inquiry_submit`.
- Franchise final website events: `franchise_inquiry_submit` and `real_estate_site_submit`.
- Website events stay neutral; GTM maps them to GA4, Google Ads, Meta, and future server-side destinations.
- Franchise Canada Form `1` specifically preserves destination continuity by mapping neutral `franchise_inquiry_submit` to existing Google Ads primary `fr_application_submit` and Meta `Fr Application Submit`; do not revert it to secondary `fr_inquiry_submit` without paid-media signoff. Post-v54 browser QA passed for Google Ads/GA4 and Meta script execution; still confirm delayed Meta Events Manager and platform reporting receipt.
- Keep Gravity Forms Measurement Protocol audit-only unless explicitly approved as a final source.
- Keep parent, franchise Canada, and franchise USA separated by property, hostname, GA4 property, and platform mapping.

## BigQuery / Dashboard Registry

- Current conversion-tracking rule references are available to dashboards through `marketing-api-488017.mart_marketing.vw_measurement_rule_registry_current`.
- The BigQuery implementation is documented in [Dashboard source layer, GreenRope, and rule registry](../20-bigquery/dashboard-source-layer-greenrope-and-rule-registry-2026-05-03.md).
- Do not upload a conversion-tracking rule as `Verified` unless the owning source doc and live evidence support that status.

## Where To Add New Files

Use this folder for new tracking-wide docs. If the doc is specifically parent/franchise and an existing phase folder already exists, use that phase folder instead and link it here.
