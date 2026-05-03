# Business Truth And Tracking Data Gaps

Last updated: 2026-05-03

## Purpose

This file records the current conversion-tracking data gaps that affect whether CEFA dashboards can treat reported inquiry counts as business truth. It is intentionally limited to tracking and conversion-data reliability; paid-media platform availability belongs in `docs/50-paid-media/`.

## Scope

| Field | Value |
|---|---|
| Workstream | Conversion tracking |
| Properties | `cefa.ca`, `franchise.cefa.ca`, `www.franchisecefa.com` |
| Systems | GTM, GA4, Google Ads, Meta, BigQuery, collector/CRM inquiry marts |
| Verification date | 2026-05-03 |
| Live writes made | No |

## Current Verified Status

| Area | Status | Current state |
|---|---|---|
| Parent final website event contract | Verified | Current repo rules identify parent final submit as `school_inquiry_submit`. |
| Franchise final website event contract | Verified | Current repo rules identify franchise final submits as `franchise_inquiry_submit` and `real_estate_site_submit`. |
| Gravity Forms Measurement Protocol role | Verified | Current repo rules keep Measurement Protocol audit-only unless explicitly approved as the final conversion source. |
| Failed/replay job queues | Verified | `cefa_ops.failed_jobs` has 0 rows and `cefa_ops.replay_jobs` has 0 rows in the checked BigQuery state. |
| Parent inquiry business-truth marts | Partial | `fct_parent_inquiries_daily` and `fct_parent_inquiries_by_location_daily` are present but max out at 2026-03-29. |
| Franchise lead-source mart | Partial | `fct_franchise_lead_sources_daily` is present but maxes out at 2026-03-29 and has only 7 checked rows. |
| GA4 traffic/event marts | Partial | GA4 traffic/event marts are populated through 2026-05-02 for traffic/event analysis, but GA4 inquiry/key-event metrics are not yet reliable as business truth. |
| GA4 Data API runtime access | Pending | Runtime service account access to the GA4 Data API is still missing; warehouse refresh currently uses the native GA4 BigQuery export path where available. |

## Conversion Data Surfaces

| Surface | Status | Min date | Max date | Rows | Notes |
|---|---:|---:|---:|---:|---|
| `mart_marketing_parents.fct_parent_inquiries_daily` | Partial | 2025-08-27 | 2026-03-29 | 7,911 | Present but stale for current reporting. |
| `mart_marketing_parents.fct_parent_inquiries_by_location_daily` | Partial | 2025-08-27 | 2026-03-29 | 7,911 | Present but stale for current location reporting. |
| `mart_marketing_franchise.fct_franchise_lead_sources_daily` | Partial | 2026-03-29 | 2026-03-29 | 7 | Present but not current enough for franchise reporting. |
| `cefa_ops.failed_jobs` | Verified | Not applicable | Not applicable | 0 | No failed jobs in checked state. |
| `cefa_ops.replay_jobs` | Verified | Not applicable | Not applicable | 0 | No replay jobs in checked state. |

## Tracking Interpretation Rules

| Rule | Status | Notes |
|---|---|---|
| Website final events remain neutral | Verified | Website events should stay neutral and GTM should map them to GA4, Google Ads, Meta, and future server-side destinations. |
| Platform conversions are not final business truth | Verified | Platform conversion counts can support platform QA and paid-media reporting, but CRM/collector/BigQuery reconciliation is still required for final inquiry truth. |
| GA4 traffic is usable before GA4 inquiry truth is final | Partial | GA4 sessions, users, source/medium, landing page, and event trend analysis are available. GA4 final inquiry counts need reconciliation before executive use. |
| Parent and franchise boundaries stay separate | Verified | Keep parent, franchise Canada, and franchise USA separated by property, hostname, GA4 property, GTM container, and platform mapping. |

## Current Gaps

| Gap | Status | Owner workstream | Notes |
|---|---|---|---|
| Current parent inquiry business truth after 2026-03-29 | Pending | Conversion tracking | Refresh or reconnect the collector/CRM/KinderTales-backed inquiry source before treating parent inquiry dashboards as current. |
| Current franchise lead-source reporting after 2026-03-29 | Pending | Conversion tracking | Refresh or reconnect franchise lead-source data before current franchise reporting. |
| GA4 Data API runtime access | Pending | Conversion tracking and BigQuery | Grant the runtime service account access or remove GA4 Data API as a required refresh dependency if native export is the chosen path. |
| Final event-to-platform reconciliation | Pending | Conversion tracking and paid media | Reconcile `school_inquiry_submit`, `franchise_inquiry_submit`, and `real_estate_site_submit` through GTM, GA4, Google Ads, Meta, and BigQuery. |
| Offline conversion export readiness | Pending | Conversion tracking and BigQuery | Requires current business-truth inquiry data, stable event IDs, and platform-safe upload contracts. |

## Next Actions

| Priority | Status | Action |
|---|---|---|
| 1 | Pending | Refresh the parent inquiry marts and prove max dates move past 2026-03-29. |
| 2 | Pending | Refresh the franchise lead-source mart and prove current franchise rows are available. |
| 3 | Pending | Run a final-event reconciliation pass from website event through GTM, GA4, Google Ads, Meta, and BigQuery for each property. |
| 4 | Pending | Decide the GA4 Data API service-account path and document the final refresh dependency. |
| 5 | Pending | Build the offline conversion export plan only after business-truth data is current and event identity is stable. |

## Source Evidence

- Verified through current repo governance/tracking docs and BigQuery checks in `marketing-api-488017` on 2026-05-03.
- No live tracking tags, platform settings, WordPress code, or GTM/GA4/Ads/Meta settings were changed by this documentation update.
