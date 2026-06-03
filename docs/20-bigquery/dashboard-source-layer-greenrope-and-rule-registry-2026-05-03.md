# Dashboard Source Layer, GreenRope, And Rule Registry

Last updated: 2026-05-04

## Purpose

Document the BigQuery resources created so CEFA dashboards can read governed reporting data without depending on a periodically renewed personal `gcloud` login, and so GreenRope and measurement/naming rules can be surfaced in dashboards without copying full lead/contact payloads.

This is a BigQuery/data workstream document. It does not redefine conversion events, Meta naming tokens, or school identity rules.

Important GreenRope label rule: the CRM aggregate is a current-state opportunity aggregate bucketed by opportunity created date. It contains `ad-attributed current inquiry-phase opportunities`, not solid paid-media inquiry truth. Do not label this metric as plain `paid inquiries` in dashboards.

## Scope

| Field | Value |
|---|---|
| Workstream | BigQuery and reporting data |
| Project | `marketing-api-488017` |
| Verification date | 2026-05-04 |
| Live BigQuery writes made | Yes |
| Live ad platform / tracking writes made | No |

## Dashboard Auth Layer

| Resource | Status | Notes |
|---|---|---|
| `cefa-dashboard-bq-reader@marketing-api-488017.iam.gserviceaccount.com` | Verified | Created as the dashboard read identity. |
| Project IAM `roles/bigquery.jobUser` | Verified | Granted to the dashboard service account so it can run query jobs. |
| Dataset read access on `mart_marketing` | Verified | Granted through dataset ACL so the dashboard can read reporting views/tables. |
| Dataset read access on `cefa_core` | Verified | Granted through dataset ACL so the dashboard can read the rule registry backing table via the mart view. |
| Service-account-key file | Verified absent by design | No JSON key was created. Preferred production path is Cloud Run service identity or another keyless workload identity path. |

Dashboard implementation rule:

- Use server-side BigQuery access from the dashboard backend/API.
- Do not expose BigQuery credentials to browser JavaScript.
- If deployed on Cloud Run, attach `cefa-dashboard-bq-reader` as the service identity.
- If deployed outside Google Cloud, prefer Workload Identity Federation. A service-account key should be a last resort and must stay out of git.

## Dashboard Views

| View | Status | Use |
|---|---|---|
| `mart_marketing.vw_school_marketing_dashboard_daily` | Verified existing | Current core school marketing dashboard daily source. |
| `mart_marketing.vw_school_marketing_looker_contract_daily` | Verified existing | Current Looker/reporting contract source. |
| `mart_marketing.vw_school_marketing_dashboard_with_crm_daily` | Verified updated | Dashboard daily source with GreenRope current-state aggregate fields, explicit zero-fill behavior, and `greenrope_join_reason`. |
| `mart_marketing.vw_greenrope_school_funnel_school_daily` | Verified updated | School-level view over the GreenRope daily group aggregate and mapping bridge; unsafe duplicate mappings keep school-level metrics null. |
| `mart_marketing.vw_measurement_rule_registry_current` | Verified new | Dashboard-safe view for active/current conversion-tracking and naming-convention rules. |

## GreenRope Daily Aggregate

| Resource | Status | Current state |
|---|---|---|
| `mart_marketing.bridge_greenrope_group_school` | Partial | Loaded 53 school mapping rows from the local GreenRope group map plus `mart_marketing.dim_school`. One duplicate CRM group mapping exists. |
| `mart_marketing.fct_greenrope_school_funnel_daily` | Verified extraction count; partial business interpretation | Loaded 6,390 daily group rows from GreenRope `GetOpportunitiesRequest`. Date range is 2025-06-12 through 2026-05-03. It is a current-state opportunity aggregate, not final lead/tour/enrollment truth. |
| GreenRope groups attempted | Verified | 52 unique CRM groups were requested. |
| GreenRope API result | Verified | 52 groups succeeded, 0 failed. |
| Raw opportunity count used for aggregation | Verified | 24,916 opportunities were counted into daily aggregate rows. |
| Stored payload level | Verified | Counts only. Full contact records, full opportunity payloads, emails, phone numbers, notes, and post bodies were not loaded into BigQuery. |
| Missing created-date count | Verified | 0 missing created dates in this extraction. |

The physical daily aggregate includes legacy first-load field names:

- `raw_opportunity_count`
- `inquiries_total`
- `paid_inquiries`
- `non_paid_inquiries`
- `tour_phase_count`
- `enrollment_phase_count`
- extraction metadata and warnings

The dashboard-facing views expose safer semantic aliases:

- `greenrope_opportunity_created_date`
- `greenrope_opportunities_created`
- `greenrope_current_inquiry_phase_opportunities`
- `greenrope_ad_attributed_current_inquiry_phase_opportunities`
- `greenrope_no_detected_ad_attribution_current_inquiry_phase_opportunities`
- `greenrope_current_tour_phase_opportunities`
- `greenrope_current_enrollment_phase_opportunities`
- `greenrope_join_reason`
- `greenrope_metrics_zero_filled`

Legacy dashboard aliases such as `greenrope_inquiries_total`, `greenrope_ad_attributed_inquiries`, `greenrope_tour_phase_count`, and `greenrope_enrollment_phase_count` remain for compatibility only.

The aggregate does not include:

- contact names
- emails
- phone numbers
- raw opportunity JSON
- CRM notes
- post/email bodies

## GreenRope Mapping Boundary

| Mapping fact | Status | Notes |
|---|---|---|
| GreenRope group IDs | Partial | Available from local `agentic-brain/src/config/greenrope-group-map.ts`; loaded to BigQuery bridge. |
| GreenRope group `50` | Partial | Maps to both `South Surrey - Morgan Crossing` and `South Surrey - Morgan Crossing East`. The dashboard-safe flag is `false` for that duplicate group so totals are not silently doubled. |
| Test location group `14` | Partial | Present in the local map as `Test Location - Summer Campaign`, but not loaded to the school bridge because it does not map to a current `mart_marketing.dim_school` school row. |

Dashboard rule:

- Treat `greenrope_dashboard_safe_mapping = true` as safe for school-level CRM totals.
- Treat duplicate group mappings as a drilldown/mapping issue, not as additive school totals.
- For duplicate mappings, dashboard-safe metric fields remain null even when source group data exists.
- For safe mappings with no GreenRope row for the created-date bucket, the dashboard view zero-fills metrics and sets `greenrope_join_reason = safe_mapping_no_opportunities_for_created_date`.

## Rule Registry

| Resource | Status | Current state |
|---|---|---|
| `cefa_core.measurement_rule_registry` | Verified | Created and seeded with 5 current conversion-tracking/naming-convention rule references. |
| `mart_marketing.vw_measurement_rule_registry_current` | Verified | Dashboard-safe current rule view. |

Seeded rule families:

| Rule family | Rows | Status |
|---|---:|---|
| `conversion_tracking` | 3 | Verified/active references to current governed docs. |
| `naming_convention` | 2 | One active local-listing rule and one `ready_for_upload` Meta NC1 reference. |

Future upload rule:

- Add new conversion-tracking or naming-convention rules to the narrowest correct docs folder first.
- Upload the dashboard-facing version to `cefa_core.measurement_rule_registry`.
- Keep `verification_status` as `Pending`, `Partial`, `Verified`, or `Open question`.
- Do not make dashboard rows look verified unless the source doc and live/platform evidence support it.

## Verification Queries

The dashboard service account was used to query these surfaces successfully:

| Query | Result |
|---|---|
| `vw_measurement_rule_registry_current` row count | 5 rows |
| `fct_greenrope_school_funnel_daily` coverage | 6,390 rows, 2025-06-12 through 2026-05-03 |
| `fct_greenrope_school_funnel_daily` totals | 24,916 opportunities counted, 15,352 current inquiry-phase opportunities, 2,898 ad-attributed current inquiry-phase opportunities, 840 current tour-phase opportunities, 904 current enrollment-phase opportunities |
| `vw_school_marketing_dashboard_with_crm_daily` all-row join reasons | 6,144 `greenrope_metrics_available`, 5,484 `safe_mapping_no_opportunities_for_created_date`, 456 `duplicate_greenrope_group_mapping`, 0 `no_greenrope_group_mapping` |
| `vw_school_marketing_dashboard_with_crm_daily` dashboard-safe current-state totals | 24,508 opportunities created, 15,298 current inquiry-phase opportunities, 2,876 ad-attributed current inquiry-phase opportunities, 817 current tour-phase opportunities, 879 current enrollment-phase opportunities |
| Dashboard reader service account query after view update | 106 rows and 130 `greenrope_opportunities_created` for 2026-05-01 through 2026-05-03 |

Metric definitions and endpoint mappings are documented in `docs/20-bigquery/greenrope-metric-definitions-and-api-map-2026-05-03.md`.
The 2026-05-04 view correction is documented in `docs/20-bigquery/greenrope-current-state-aggregate-corrections-2026-05-04.md`.

## Cost Snapshot

| Usage area | Status | Current value |
|---|---|---:|
| May 2026 query usage after the 2026-05-04 GreenRope verification | Verified | 13.8818 GiB |
| Share of 1 TiB monthly free query tier | Verified | About 1.356 percent |
| May 2026 query job count after the 2026-05-04 GreenRope verification | Verified | 469 jobs |
| Logical storage after the 2026-05-03 physical writes | Verified snapshot | 0.9679 GiB |
| Share of 10 GiB free storage tier | Verified snapshot | About 9.68 percent |

This work stayed well inside the BigQuery free query and storage tier based on the checked state. The 2026-05-04 GreenRope correction replaced views only, so it did not materially add stored data.

## Current Gaps

| Gap | Status | Owner workstream | Notes |
|---|---|---|---|
| GreenRope refresh automation | Pending | BigQuery and CRM/source systems | The first load was manual. A scheduled refresh job should be added if the dashboard will rely on this daily. |
| Duplicate GreenRope group `50` | Partial | Master data and BigQuery | Needs a business decision before dashboard totals can split or attribute that CRM group across the two South Surrey rows. |
| Raw or restricted GreenRope opportunities table | Pending | BigQuery and CRM/source systems | Needed to audit exact source phase strings, date fields, and custom-field matching from warehouse-visible evidence. |
| Normalized GreenRope opportunity table | Pending | BigQuery and CRM/source systems | Needed for a stable PII-aware opportunity layer and future historical/current-state metrics. |
| GreenRope field dictionary and phase/path snapshots | Pending | BigQuery and CRM/source systems | `GetOpportunityFieldsRequest`, `GetPhasesRequest`, and `GetPhasePathsRequest` are required before the definitions are fully governed. |
| Google Ads/Supermetrics freshness after 2026-04-30 | Open question | BigQuery and paid media | Still unresolved from the warehouse current-state doc. |
| Parent/franchise business-truth marts after 2026-03-29 | Pending | Conversion tracking and BigQuery | GreenRope daily aggregate helps CRM visibility but does not replace the stale parent/franchise marts yet. |
| Rule registry upload workflow | Pending | BigQuery, conversion tracking, naming convention | Tables/views exist and seed rows are loaded; future rules still need a repeatable upload script or controlled process. |
| GreenRope ad-attributed current inquiry-phase confidence | Partial | BigQuery and paid media | The CRM metric is based on UTM/click-id fields in GreenRope opportunities. It is not final paid-media truth until reconciled to Google Ads/Meta and spend/import data. |

## Source Evidence

- Verified through live BigQuery, IAM, and GreenRope API checks on 2026-05-03 and live BigQuery view checks on 2026-05-04.
- GreenRope credentials were read from local env only and were not copied into repo docs or logs.
- No full GreenRope lead/contact payloads were committed or loaded to BigQuery.
