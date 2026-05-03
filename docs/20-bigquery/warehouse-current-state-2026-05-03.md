# BigQuery Warehouse Current State

Last updated: 2026-05-03

## Purpose

This file records the current verified BigQuery, warehouse, dashboard, QA, and cost state for CEFA school marketing reporting. It is the BigQuery/data workstream status surface, not a paid-media optimization or conversion-tracking implementation plan.

## Scope

| Field | Value |
|---|---|
| Workstream | BigQuery and reporting data |
| Project | `marketing-api-488017` |
| Primary datasets | `analytics_267558140`, `raw_ga4`, `raw_google_ads`, `raw_meta_ads`, `raw_supermetrics`, `mart_marketing`, `mart_marketing_parents`, `mart_marketing_franchise`, `cefa_ops` |
| Verification date | 2026-05-03 |
| Live writes made by this BigQuery readiness update | Yes: dashboard reader identity, GreenRope aggregate tables/views, and measurement rule registry |
| Warehouse refresh observed | Verified Cloud Run job execution completed on 2026-05-03 |

## Current Verified Status

| Area | Status | Current state |
|---|---|---|
| Scheduled refresh | Verified | Cloud Scheduler job is enabled on `0 6 * * *` America/Vancouver. Next scheduled run observed for 2026-05-04 13:00:00 UTC. |
| Manual refresh | Verified | Cloud Run job `cefa-school-marketing-refresh` completed successfully as execution `cefa-school-marketing-refresh-8kfvz` at 2026-05-03T18:57:27Z. |
| Dashboard daily view | Verified | `mart_marketing.vw_school_marketing_dashboard_daily` is populated from 2025-09-17 through 2026-05-02. |
| Looker contract view | Verified | `mart_marketing.vw_school_marketing_looker_contract_daily` is populated from 2025-09-17 through 2026-05-02. |
| Dashboard service auth | Verified | `cefa-dashboard-bq-reader@marketing-api-488017.iam.gserviceaccount.com` exists, has `roles/bigquery.jobUser`, and has read access to `mart_marketing` and `cefa_core`. No service-account key was created. |
| Dashboard CRM view | Verified | `mart_marketing.vw_school_marketing_dashboard_with_crm_daily` is queryable by the dashboard service account. |
| GreenRope daily aggregate | Verified | `mart_marketing.fct_greenrope_school_funnel_daily` has 6,390 daily group rows from 2025-06-12 through 2026-05-03. It stores counts only, not full lead/contact payloads. Its ad-attributed inquiry count is not solid paid-media truth. |
| Measurement rule registry | Verified | `cefa_core.measurement_rule_registry` has 5 seeded conversion-tracking/naming-convention rule references and is exposed through `mart_marketing.vw_measurement_rule_registry_current`. |
| Native GA4 export | Verified | `analytics_267558140.events_*` is available from 2026-03-11 through 2026-05-02 in the checked event-date table window. |
| GA4 Data API runtime access | Pending | Runtime service account access to the GA4 Data API is still missing; the warehouse refresh currently relies on the native GA4 BigQuery export path where available. |
| Google Ads source data | Partial | Current checked Google Ads and Supermetrics Google conversion/action rows stop at 2026-04-30. The transfer config reports successful runs for May dates, but source campaign stats have no rows after 2026-04-30. |
| Meta Ads source data | Partial | Native Meta rows are present through 2026-05-02, but the May 1 and May 2 dashboard rows contain zero paid metrics. Supermetrics Meta action/detail rows stop at 2026-04-30. |
| Parent inquiry business-truth marts | Partial | Parent inquiry marts are present but stale at 2026-03-29. |
| Franchise lead-source mart | Partial | Franchise lead-source mart is present but stale at 2026-03-29. |
| BigQuery free query tier | Verified | May 2026 query usage observed at 12.9346 GiB after the dashboard/GreenRope/rule-registry work, which is about 1.263 percent of the 1 TiB monthly free query tier. |
| BigQuery free storage tier | Verified | Logical storage observed at 0.9679 GiB, which is about 9.68 percent of the 10 GiB free storage tier. |

## Source Freshness

| Source surface | Status | Min date | Max date | Rows | Key metric check |
|---|---:|---:|---:|---:|---:|
| `analytics_267558140.events_*` | Verified | 2026-03-11 | 2026-05-02 | 53 event-date tables | Native GA4 export available through 2026-05-02. |
| `raw_google_ads` campaign stats | Partial | 2026-03-01 | 2026-04-30 | 10,249 | 34,669 clicks, 2,843.20693 conversions. |
| `raw_supermetrics` Google conversion type | Partial | 2026-03-01 | 2026-04-30 | 609 | 1,767.37 conversions. |
| `raw_supermetrics` Meta action | Partial | 2026-01-04 | 2026-04-30 | 1,671 | 3,832.0 conversions. |
| `raw_supermetrics` Meta ad set | Partial | 2026-01-03 | 2026-04-30 | 4,302 | 72,802 outbound clicks. |
| `raw_meta_ads` native ad insights | Partial | 2026-01-01 | 2026-05-02 | 6,493 | 178,490 clicks. |

## Dashboard And Looker Contract Coverage

| Surface | Status | Min date | Max date | Rows | Schools | GA sessions | Google inquiries | Meta inquiries |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `mart_marketing.fact_school_marketing_context_daily` | Verified | 2025-09-17 | 2026-05-02 | 12,084 | 53 | 38,910 | 817 | 2,941 |
| `mart_marketing.vw_school_marketing_dashboard_daily` | Verified | 2025-09-17 | 2026-05-02 | 12,084 | 53 | 38,910 | 817 | 2,941 |
| `mart_marketing.vw_school_marketing_dashboard_with_crm_daily` | Verified | 2025-09-17 | 2026-05-02 | 12,084 | 53 | 38,910 | 817 | 2,941 |
| `mart_marketing.vw_school_marketing_looker_contract_daily` | Verified | 2025-09-17 | 2026-05-02 | 80,678 | 53 | 38,910 | 817 | 2,941 |

## Mart Coverage

| Mart | Status | Min date | Max date | Rows | Schools |
|---|---:|---:|---:|---:|---:|
| `fact_ga4_daily` | Verified | 2026-03-01 | 2026-05-02 | 2,684 | 45 |
| `fact_ga4_event_daily` | Verified | 2026-03-01 | 2026-05-02 | 20,808 | 45 |
| `fact_ga4_landing_page_daily` | Verified | 2026-03-01 | 2026-05-02 | 2,684 | 45 |
| `fact_ga4_source_medium_daily` | Verified | 2026-03-01 | 2026-05-02 | 8,767 | 45 |
| `fact_google_ads_daily` | Partial | 2026-03-05 | 2026-04-30 | 741 | 16 |
| `fact_google_ads_conversion_type_daily` | Partial | 2026-03-09 | 2026-04-30 | 409 | 16 |
| `fact_google_ads_ad_group_daily` | Partial | 2026-03-05 | 2026-04-30 | 3,342 | 16 |
| `fact_google_ads_keyword_daily` | Partial | 2026-03-05 | 2026-04-30 | 14,078 | 16 |
| `fact_meta_ads_daily` | Partial | 2026-01-01 | 2026-05-02 | 1,739 | 20 |
| `fact_meta_ads_conversion_type_daily` | Partial | 2026-01-04 | 2026-04-30 | 1,234 | 19 |
| `fact_meta_ads_ad_set_daily` | Partial | 2026-01-03 | 2026-04-30 | 2,827 | 19 |
| `fact_meta_ads_creative_daily` | Partial | 2026-01-03 | 2026-04-30 | 9,281 | 19 |
| `fct_greenrope_school_funnel_daily` | Verified | 2025-06-12 | 2026-05-03 | 6,390 | 52 CRM groups |

## Latest Seven-Day Dashboard Context

| Date | Status | Rows | Schools | Google inquiries | Meta inquiries | GA sessions | Paid spend |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-04-26 | Verified | 53 | 53 | 13 | 18 | 707 | 1,329.38104 |
| 2026-04-27 | Verified | 53 | 53 | 35 | 49 | 1,127 | 2,445.490128 |
| 2026-04-28 | Verified | 53 | 53 | 8 | 42 | 902 | 2,036.550164 |
| 2026-04-29 | Verified | 53 | 53 | 13 | 38 | 787 | 1,722.114089 |
| 2026-04-30 | Verified | 53 | 53 | 9 | 11 | 169 | 822.971002 |
| 2026-05-01 | Partial | 53 | 53 | 0 | 0 | 8 | 0 |
| 2026-05-02 | Partial | 53 | 53 | 0 | 0 | 4 | 0 |

May 1 and May 2 are marked `Partial` because the context view has rows for all 53 schools, but paid media metrics are zero while source availability is uneven across platform feeds.

## Looker Contract Fields

`vw_school_marketing_looker_contract_daily` currently exposes these field groups.

| Field group | Status | Fields |
|---|---|---|
| Record, platform, school, location, and time dimensions | Verified | `record_type`, `platform`, `school_id`, `canonical_location_id`, `location_code`, `location_name`, `school_slug`, `timezone`, `landing_page_path`, `date`, `month`, `date_range_start`, `date_range_end` |
| Detail dimensions | Verified | `conversion_type`, `ad_group`, `search_keyword`, `ad_set_name`, `creative_image_url`, `ad_name`, `ad_body`, `session_source_medium`, `event_name`, `landing_page` |
| Paid and GA4 metrics | Verified | `google_amount_spent`, `google_inquiry_submit`, `meta_amount_spent`, `meta_inquiry_submit`, `ga_total_users`, `ga_sessions`, `ga_engaged_sessions`, `ga_session_cvr`, `primary_funnel_inquiries`, `total_paid_spend`, `total_paid_inquiries`, `blended_cpl`, `crm_gap`, `website_demand`, `amount_spent`, `cost`, `avg_cpm`, `cpm`, `impressions`, `ctr`, `clicks`, `avg_cpc`, `cpc`, `conversions`, `inquiry_submit`, `conv_rate`, `conversion_rate`, `cost_per_inquiry`, `cost_per_conversion`, `total_users`, `new_users`, `sessions`, `session_duration`, `average_session_duration`, `engagement_rate`, `engaged_sessions`, `event_count`, `key_events`, `session_cvr`, `last_updated_at` |

## QA Checks

| Check group | Status | Result |
|---|---|---|
| Duplicate checks | Verified | 0 duplicate key groups across checked context, dashboard, Google Ads, Meta Ads, GA4, and raw refresh windows. |
| Integrity checks | Verified | 0 issue counts for null context keys, orphan school joins, duplicate/null `dim_school` IDs, latest-window missing context school dates, and negative GA4/Google/Meta metrics. |
| Failed refresh/replay jobs | Verified | `cefa_ops.failed_jobs` has 0 rows and `cefa_ops.replay_jobs` has 0 rows in the checked state. |

Duplicate checks were run for these keys: context school/date, dashboard school/date, Google daily school/date, Google conversion school/date/type, Google ad group school/date/group, Google keyword school/date/keyword, Meta daily school/date, Meta conversion school/date/type, Meta ad set school/date/name, Meta creative school/date/key, GA4 daily school/date, GA4 event school/date/event, GA4 source school/date/source, GA4 landing school/date/page, raw Google conversion window, raw Meta action window, and raw Meta ad set window.

## Table Design

| Surface | Status | Current structure |
|---|---|---|
| `mart_marketing.fact_*` dashboard fact tables | Verified | Tables are partitioned by `date`. Cluster keys are aligned to the main query grain, such as `school_id`, `school_id, conversion_type`, `school_id, ad_group`, `school_id, keyword_text`, `school_id, ad_set_name`, `school_id, creative_key`, `school_id, landing_page`, `school_id, session_source_medium`, and `school_id, event_name`. |
| `raw_supermetrics.*` refresh tables | Verified | Tables are partitioned by `report_date` and clustered by account, campaign, or detail keys. |
| `fct_greenrope_school_funnel_daily` | Verified | Table is partitioned by `snapshot_date` and clustered by `greenrope_group_id`. It stores aggregate counts only. |
| `measurement_rule_registry` | Verified | Table is clustered by `rule_family`, `rule_scope`, and `lifecycle_status`; dashboard reads use the current-rule mart view. |
| `mart_marketing.dim_school` | Verified | Small dimension table is unpartitioned, which is appropriate for its size and use. |
| `vw_school_marketing_dashboard_daily`, `vw_school_marketing_dashboard_with_crm_daily`, `vw_school_marketing_looker_contract_daily`, and `vw_measurement_rule_registry_current` | Verified | Views, not physical tables. |

## Free Tier Usage

| Usage area | Status | Current value |
|---|---:|---:|
| May 2026 query usage | Verified | 12.9346 GiB |
| Share of 1 TiB monthly free query tier | Verified | About 1.263 percent |
| May 2026 query job count | Verified | 408 jobs |
| 2026-05-03 query usage | Verified | 12.4932 GiB |
| 2026-05-03 query job count | Verified | 331 jobs |
| Logical storage | Verified | 0.9679 GiB |
| Share of 10 GiB free storage tier | Verified | 9.68 percent |
| Table count | Verified | 299 tables |

The current verified state is not close to the free query or free storage limits. Continue using targeted checks and partition filters to preserve this margin.

## Current Gaps

| Gap | Status | Owner workstream | Notes |
|---|---|---|---|
| GA4 Data API access for refresh service account | Pending | BigQuery and conversion tracking | Native GA4 BigQuery export is working, but service account GA4 Data API access still needs to be granted or intentionally removed from the runtime path. |
| Google Ads rows after 2026-04-30 | Open question | BigQuery and paid media | Data Transfer runs report success for May dates, but campaign stats have no rows after 2026-04-30. Confirm whether this is source-side zero activity, delayed source data, account selection, or transfer mapping. |
| Supermetrics Google and Meta detail after 2026-04-30 | Open question | BigQuery and paid media | Supermetrics conversion/action detail tables stop at 2026-04-30 in the checked state. |
| Parent inquiry business-truth marts after 2026-03-29 | Pending | Conversion tracking and BigQuery | Parent inquiry marts need the current collector/CRM/export path refreshed before dashboards can treat them as current business truth. |
| Franchise lead-source mart after 2026-03-29 | Pending | Conversion tracking and BigQuery | Franchise lead-source reporting needs a refreshed data source before use in current reporting. |
| GA4 key-event inquiry metrics in school marketing marts | Partial | Conversion tracking and BigQuery | GA4 school marketing marts are populated for traffic/event analysis, but inquiry metrics are not yet reliable as business truth. |
| GreenRope refresh automation | Pending | BigQuery and CRM/source systems | First GreenRope daily aggregate load was manual. Add a scheduled refresh before dashboards depend on it daily. |
| Duplicate GreenRope group `50` | Partial | BigQuery and master data | Group `50` maps to both South Surrey Morgan Crossing rows. Dashboard-safe CRM fields are withheld for duplicate group mappings to avoid silent double-counting. |
| Rule registry upload workflow | Pending | BigQuery, conversion tracking, naming convention | Tables/views and seed rows exist. A repeatable upload process is still needed for future rule changes. |
| GreenRope ad-attributed inquiry definition | Partial | BigQuery and paid media | Dashboard views expose `greenrope_ad_attributed_inquiries`; this means GreenRope inquiry rows with UTM/click-id markers, not platform-confirmed paid inquiries. |

## Next Actions

| Priority | Status | Action |
|---|---|---|
| 1 | Pending | Confirm why Google Ads source rows stop at 2026-04-30 despite successful transfer runs. |
| 2 | Pending | Refresh or rebuild the parent inquiry and franchise lead-source business-truth marts. |
| 3 | Pending | Decide whether GA4 Data API service-account access should be repaired or removed from the refresh dependency list. |
| 4 | Pending | Add a repeatable low-cost QA script or saved query set for the duplicate, integrity, freshness, and free-tier checks listed here. |
| 5 | Pending | Document the Looker dashboard contract in a stable schema file if downstream dashboards depend on exact field names. |
| 6 | Pending | Automate the GreenRope daily aggregate refresh and rule-registry upload workflow if dashboards will depend on those surfaces. |

## Source Evidence

- Verified through BigQuery, Cloud Run, Cloud Scheduler, and Data Transfer checks run against `marketing-api-488017` on 2026-05-03.
- Dashboard source layer details are documented in `docs/20-bigquery/dashboard-source-layer-greenrope-and-rule-registry-2026-05-03.md`.
- GreenRope metric definitions and API endpoint mappings are documented in `docs/20-bigquery/greenrope-metric-definitions-and-api-map-2026-05-03.md`.
- Sensitive Data Transfer configuration values were not copied into this document.
