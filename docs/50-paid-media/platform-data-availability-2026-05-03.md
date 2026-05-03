# Paid Media Platform Data Availability

Last updated: 2026-05-03

## Purpose

This file records current paid-media source freshness, reporting availability, and platform-data gaps for CEFA dashboards. It does not approve budget, campaign, bidding, or naming changes.

## Scope

| Field | Value |
|---|---|
| Workstream | Paid media execution |
| Platforms | Google Ads, Meta Ads, Supermetrics, BigQuery Data Transfer |
| Reporting project | `marketing-api-488017` |
| Verification date | 2026-05-03 |
| Live writes made | No |

## Current Verified Status

| Area | Status | Current state |
|---|---|---|
| Google Ads transfer config | Verified | `google_ads_daily_primary` is enabled, scheduled every 24 hours, and recent transfer runs report `SUCCEEDED`. |
| Meta Ads transfer config | Verified | `facebook_ads_daily_primary` is enabled, scheduled every 24 hours, and recent transfer runs report `SUCCEEDED`. |
| Google Ads campaign stats in warehouse | Partial | Rows are present from 2026-03-01 through 2026-04-30. No checked campaign stats rows exist after 2026-04-30. |
| Google conversion-type detail via Supermetrics | Partial | Rows are present from 2026-03-01 through 2026-04-30. |
| Meta native ad insights | Partial | Native rows are present from 2026-01-01 through 2026-05-02. May 1 and May 2 dashboard metrics are zero. |
| Meta action/detail via Supermetrics | Partial | Meta action and ad-set detail rows stop at 2026-04-30 in the checked state. |
| Paid dashboard availability | Partial | Dashboard context rows exist through 2026-05-02, but paid metrics are current only through 2026-04-30 for Google and Supermetrics detail. |
| Business-truth conversion use | Pending | Platform conversions should not be treated as final business truth until CRM/collector/BigQuery inquiry reconciliation is refreshed. |

## Platform Source Freshness

| Source surface | Status | Min date | Max date | Rows | Key metric check |
|---|---:|---:|---:|---:|---:|
| Google Ads campaign stats | Partial | 2026-03-01 | 2026-04-30 | 10,249 | 34,669 clicks, 2,843.20693 platform conversions. |
| Google Ads conversion type via Supermetrics | Partial | 2026-03-01 | 2026-04-30 | 609 | 1,767.37 conversion-type conversions. |
| Meta action via Supermetrics | Partial | 2026-01-04 | 2026-04-30 | 1,671 | 3,832.0 action conversions. |
| Meta ad set via Supermetrics | Partial | 2026-01-03 | 2026-04-30 | 4,302 | 72,802 outbound clicks. |
| Meta native ad insights | Partial | 2026-01-01 | 2026-05-02 | 6,493 | 178,490 clicks. |

## Dashboard Paid Metrics

| Date | Status | Google inquiries | Meta inquiries | Paid spend |
|---|---:|---:|---:|---:|
| 2026-04-26 | Verified | 13 | 18 | 1,329.38104 |
| 2026-04-27 | Verified | 35 | 49 | 2,445.490128 |
| 2026-04-28 | Verified | 8 | 42 | 2,036.550164 |
| 2026-04-29 | Verified | 13 | 38 | 1,722.114089 |
| 2026-04-30 | Verified | 9 | 11 | 822.971002 |
| 2026-05-01 | Partial | 0 | 0 | 0 |
| 2026-05-02 | Partial | 0 | 0 | 0 |

May 1 and May 2 are not safe for paid-media performance interpretation yet because platform source coverage is incomplete and dashboard paid metrics are zero.

## Transfer Status

| Transfer config | Status | Dataset | Schedule | Recent state |
|---|---|---|---|---|
| `google_ads_daily_primary` | Verified | `raw_google_ads` | Every 24 hours | Recent runs report `SUCCEEDED`, including the run for 2026-05-02. |
| `facebook_ads_daily_primary` | Verified | `raw_meta_ads` | Every 24 hours | Recent runs report `SUCCEEDED`, including the run for 2026-05-02. |

Sensitive OAuth, client, token, or secret values from transfer configs must not be copied into this repo.

## Guardrails

| Rule | Status | Notes |
|---|---|---|
| Budget changes | Verified | Do not change live budgets from spreadsheet math or these dashboard totals alone. |
| Bidding changes | Verified | Do not change live campaigns, conversion goals, bidding, or campaign settings without explicit approval. |
| Business truth | Verified | Platform-reported conversions are useful for platform QA and directional paid reporting, but are not final business truth while CRM/collector reconciliation is unresolved. |
| Micro-conversions | Verified | Keep micro-conversions out of Google Ads bidding unless CEFA explicitly changes that decision. |
| Naming changes | Verified | Naming changes belong in `docs/40-naming-convention/` and must not be inferred from this platform availability file. |

## Current Gaps

| Gap | Status | Owner workstream | Notes |
|---|---|---|---|
| Google Ads rows after 2026-04-30 | Open question | Paid media and BigQuery | Determine whether this is true zero activity, source delay, account coverage, transfer mapping, or a reporting-window issue. |
| Supermetrics conversion/action detail after 2026-04-30 | Open question | Paid media and BigQuery | Supermetrics detail needs a targeted refresh or source check before May reporting. |
| Meta May paid metrics | Open question | Paid media and BigQuery | Native rows exist through 2026-05-02, but dashboard paid metrics are zero for May 1 and May 2. |
| Platform conversions vs. CRM inquiries | Pending | Paid media and conversion tracking | Reconcile platform inquiry counts against refreshed business-truth marts before using them for executive reporting. |

## Next Actions

| Priority | Status | Action |
|---|---|---|
| 1 | Pending | Run a narrow Google Ads source check for 2026-05-01 through 2026-05-03 before May pacing/reporting decisions. |
| 2 | Pending | Run a narrow Supermetrics Google and Meta detail check for rows after 2026-04-30. |
| 3 | Pending | Confirm Meta native May rows have expected spend/action fields, not just insight-row presence. |
| 4 | Pending | Link final conversion-action definitions back to `docs/10-conversion-tracking/` once the refreshed business-truth source is current. |

## Source Evidence

- Verified through BigQuery Data Transfer, BigQuery raw-source, Supermetrics-derived table, and mart checks in `marketing-api-488017` on 2026-05-03.
- No live platform settings were changed.
