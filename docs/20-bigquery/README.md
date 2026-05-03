# BigQuery And Data Workstream

This folder is for CEFA warehouse, reporting, and data-contract work connected to conversion tracking and paid media.

## Local Source References

- `/Users/matthewbison/Desktop/cefa-nexus/CEFA/.agency/plans/school-marketing-bigquery-plan-2026-04-03.md`
- `/Users/matthewbison/Desktop/cefa-nexus/CEFA/.agency/context/school-marketing-looker-studio-bq-gap-assessment-2026-04-09.md`
- `/Users/matthewbison/Desktop/cefa-nexus/CEFA/.agency/context/school-marketing-looker-studio-metric-contract-2026-04-09.md`
- `/Users/matthewbison/Desktop/cefa-nexus/CEFA/.agency/context/warehouse-refresh-automation-2026-04-20.md`

## Current Known Warehouse Surfaces

- Parent GA4 export: `marketing-api-488017.analytics_267558140.events_*`
- School dimension: `marketing-api-488017.mart_marketing.dim_school`
- Parent/franchise marts: `mart_marketing`, `mart_marketing_parents`, `mart_marketing_franchise`
- Raw sources: `raw_ga4`, `raw_google_ads`, `raw_meta_ads`, `raw_supermetrics`

## Current Files

- [Warehouse current state, QA, freshness, and free-tier usage, 2026-05-03](./warehouse-current-state-2026-05-03.md)

## Rules

- Do not create a second hand-maintained school registry if `school_uuid` / master-data tables can be reused.
- Put reusable source data in raw/staging/core/mart layers according to the existing warehouse plan.
- Keep `school_uuid` as the parent school join key unless a verified source changes the model.
- Mark sparse or incomplete marts as `Partial`, not `Verified`.

## Suggested Next Files

- `warehouse-source-index.md`
- `school-marketing-mart-contract.md`
- `offline-conversion-export-plan.md`
- `qa-checks.md`
