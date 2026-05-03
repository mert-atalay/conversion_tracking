# School Dimension Warehouse Coverage

Last updated: 2026-05-03

## Purpose

This file records the current verified school-dimension coverage used by the CEFA school marketing warehouse and dashboards. It is a master-data status note, not a tracking or paid-media implementation plan.

## Scope

| Field | Value |
|---|---|
| Workstream | Master data |
| Primary surface | `marketing-api-488017.mart_marketing.dim_school` and downstream school marketing marts/views |
| Verification date | 2026-05-03 |
| Live writes made | No |

## Current Verified Status

| Area | Status | Current state |
|---|---|---|
| Dashboard school coverage | Verified | `fact_school_marketing_context_daily`, `vw_school_marketing_dashboard_daily`, and `vw_school_marketing_looker_contract_daily` each report 53 schools in the checked state. |
| Latest context school/date coverage | Verified | Latest seven-day context checks showed 53 rows and 53 schools for each date from 2026-04-26 through 2026-05-02. |
| School dimension key health | Verified | Integrity checks returned 0 issue counts for null context keys, orphan school joins, duplicate/null `dim_school` IDs, and missing latest-window school/date context rows. |
| GA4 school coverage | Partial | GA4 daily/event/source/landing marts report 45 schools, while the dashboard context reports 53 schools. |
| Google Ads school coverage | Partial | Google Ads daily/conversion/ad-group/keyword marts report 16 schools. |
| Meta Ads school coverage | Partial | Meta Ads daily marts report 20 schools; Meta detail marts report 19 schools. |
| `canonical_location_id` maturity | Partial | Current workstream rules say `canonical_location_id` is present for checked school rows but mixed-format, so it is not yet the final normalized school key. |

## School Coverage By Surface

| Surface | Status | Schools | Notes |
|---|---:|---:|---|
| `mart_marketing.fact_school_marketing_context_daily` | Verified | 53 | Main school/date context table. |
| `mart_marketing.vw_school_marketing_dashboard_daily` | Verified | 53 | Dashboard view. |
| `mart_marketing.vw_school_marketing_looker_contract_daily` | Verified | 53 | Looker contract view. |
| GA4 marts | Partial | 45 | Traffic/event data is present for fewer schools than the full context surface. |
| Google Ads marts | Partial | 16 | Paid Google coverage reflects current campaign/source coverage, not full CEFA school universe. |
| Meta Ads daily mart | Partial | 20 | Paid Meta coverage reflects current campaign/source coverage, not full CEFA school universe. |
| Meta Ads detail marts | Partial | 19 | Ad set/conversion/creative detail coverage is one school lower than daily Meta coverage. |

## Master-Data Fields In Looker Contract

| Field group | Status | Fields |
|---|---|---|
| School and location identifiers | Verified | `school_id`, `canonical_location_id`, `location_code`, `location_name`, `school_slug`, `timezone`, `landing_page_path` |
| Time grain | Verified | `date`, `month`, `date_range_start`, `date_range_end` |
| Platform grain | Verified | `platform`, `record_type` |

## Current Known Gaps

| Gap | Status | Notes |
|---|---|---|
| Normalized final school key | Pending | `school_uuid` remains the parent tracking join key. `canonical_location_id` is useful but not final-normalized yet. |
| External system crosswalk completion | Pending | WordPress School Manager IDs, Gravity routing, school codes, CRM/KinderTales mappings, and program journey-code mappings still need the current master-data workstream to finish and verify them. |
| Paid platform school coverage | Partial | Google Ads and Meta coverage should not be interpreted as missing schools from the master list without checking live campaign/account scope. |
| GA4 school coverage difference | Open question | GA4 marts cover 45 schools while context covers 53. Confirm whether missing schools reflect no traffic, unmapped pages, or data extraction limits. |

## Next Actions

| Priority | Status | Action |
|---|---|---|
| 1 | Pending | Create or refresh `data/reference/school-crosswalk.csv` once the canonical school, platform, CRM, and website identifiers are verified. |
| 2 | Pending | Create or refresh `data/reference/program-crosswalk.csv` after program and journey-code mappings are verified. |
| 3 | Pending | Reconcile the 53-school context surface against 45-school GA4 coverage and paid-media school coverage. |
| 4 | Pending | Keep `canonical_location_id` marked partial until the final normalized key decision is documented. |

## Source Evidence

- Verified through BigQuery school marketing mart/view checks and existing master-data workstream rules on 2026-05-03.
- No reference data files were changed by this update.
