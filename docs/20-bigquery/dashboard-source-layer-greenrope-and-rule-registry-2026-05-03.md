# Dashboard Source Layer, GreenRope, And Rule Registry

Last updated: 2026-05-03

## Purpose

Document the BigQuery resources created so CEFA dashboards can read governed reporting data without depending on a periodically renewed personal `gcloud` login, and so GreenRope and measurement/naming rules can be surfaced in dashboards without copying full lead/contact payloads.

This is a BigQuery/data workstream document. It does not redefine conversion events, Meta naming tokens, or school identity rules.

## Scope

| Field | Value |
|---|---|
| Workstream | BigQuery and reporting data |
| Project | `marketing-api-488017` |
| Verification date | 2026-05-03 |
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
| `mart_marketing.vw_school_marketing_dashboard_with_crm_daily` | Verified new | Dashboard daily source with GreenRope aggregate fields joined when the CRM group has a safe one-school mapping. |
| `mart_marketing.vw_greenrope_school_funnel_school_daily` | Verified new | School-level view over the GreenRope daily group aggregate and mapping bridge. |
| `mart_marketing.vw_measurement_rule_registry_current` | Verified new | Dashboard-safe view for active/current conversion-tracking and naming-convention rules. |

## GreenRope Daily Aggregate

| Resource | Status | Current state |
|---|---|---|
| `mart_marketing.bridge_greenrope_group_school` | Partial | Loaded 53 school mapping rows from the local GreenRope group map plus `mart_marketing.dim_school`. One duplicate CRM group mapping exists. |
| `mart_marketing.fct_greenrope_school_funnel_daily` | Verified | Loaded 6,390 daily group rows from GreenRope `GetOpportunitiesRequest`. Date range is 2025-06-12 through 2026-05-03. |
| GreenRope groups attempted | Verified | 52 unique CRM groups were requested. |
| GreenRope API result | Verified | 52 groups succeeded, 0 failed. |
| Raw opportunity count used for aggregation | Verified | 24,916 opportunities were counted into daily aggregate rows. |
| Stored payload level | Verified | Counts only. Full contact records, full opportunity payloads, emails, phone numbers, notes, and post bodies were not loaded into BigQuery. |
| Missing created-date count | Verified | 0 missing created dates in this extraction. |

The daily aggregate includes:

- `raw_opportunity_count`
- `inquiries_total`
- `paid_inquiries`
- `non_paid_inquiries`
- `tour_phase_count`
- `enrollment_phase_count`
- extraction metadata and warnings

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
| `fct_greenrope_school_funnel_daily` totals | 15,352 inquiries, 840 tour-phase rows, 904 enrollment-phase rows |
| `vw_school_marketing_dashboard_with_crm_daily` for 2026-05-01 through 2026-05-03 | 106 dashboard rows, 61 GreenRope joined rows, 59 dashboard-safe CRM rows |

## Cost Snapshot

| Usage area | Status | Current value |
|---|---|---:|
| May 2026 query usage after this work | Verified | 12.9346 GiB |
| Share of 1 TiB monthly free query tier | Verified | About 1.263 percent |
| Logical storage after this work | Verified | 0.9679 GiB |
| Share of 10 GiB free storage tier | Verified | About 9.68 percent |

This work stayed well inside the BigQuery free query and storage tier based on the checked state.

## Current Gaps

| Gap | Status | Owner workstream | Notes |
|---|---|---|---|
| GreenRope refresh automation | Pending | BigQuery and CRM/source systems | The first load was manual. A scheduled refresh job should be added if the dashboard will rely on this daily. |
| Duplicate GreenRope group `50` | Partial | Master data and BigQuery | Needs a business decision before dashboard totals can split or attribute that CRM group across the two South Surrey rows. |
| Google Ads/Supermetrics freshness after 2026-04-30 | Open question | BigQuery and paid media | Still unresolved from the warehouse current-state doc. |
| Parent/franchise business-truth marts after 2026-03-29 | Pending | Conversion tracking and BigQuery | GreenRope daily aggregate helps CRM visibility but does not replace the stale parent/franchise marts yet. |
| Rule registry upload workflow | Pending | BigQuery, conversion tracking, naming convention | Tables/views exist and seed rows are loaded; future rules still need a repeatable upload script or controlled process. |

## Source Evidence

- Verified through live BigQuery, IAM, and GreenRope API checks on 2026-05-03.
- GreenRope credentials were read from local env only and were not copied into repo docs or logs.
- No full GreenRope lead/contact payloads were committed or loaded to BigQuery.
