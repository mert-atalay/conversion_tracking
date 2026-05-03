# Canonical School And Program Taxonomy Status

Last updated: 2026-05-03

## Short Answer

We have solid partial information, but not the complete cross-system canonical table requested yet.

The strongest verified school identity key is `school_uuid`. It is used by the parent inquiry URL, Gravity Forms Form 4 field `32.1`, the helper-plugin/GA4 payload as `school_selected_id`, and the current CEFA Ops school identity map. The current CEFA Ops reference also defines `school_uuid` as the current KinderTales school unique ID.

The current marketing warehouse has a populated school dimension at `marketing-api-488017.mart_marketing.dim_school` with 53 rows. It maps `school_uuid` to `canonical_location_id`, `location_code`, `location_name`, `school_slug`, `timezone`, and `landing_page_path`.

Follow-up verification on 2026-05-03 found no blank `canonical_location_id` values, but the field is mixed-format in the current warehouse table: 40 rows are UUID-like and 13 rows are slug-like. This is a normalization gap, not a missing-ID gap.

What is not yet fully proven is a single populated table that maps every school to all requested systems at once:

- WordPress School Manager internal post/object ID.
- GreenRope group/location ID.
- KinderTales ID if this is separate from `school_uuid`.
- Gravity Forms school label beyond the saved Form 4 labels.
- GA4/location label beyond `school_selected_name`, `school_selected_slug`, and `school_selected_id`.
- GBP location ID.
- ad account / campaign naming key.

The right move is to treat this document as the tracked canonical-taxonomy backlog and only promote fields to `verified` when the source table/export/API confirms them.

Concrete known-value table: [known-school-program-reference-table-2026-05-03.md](./known-school-program-reference-table-2026-05-03.md).

## Why This Matters For Tracking

School and program identity should not be inferred from labels alone. Labels can change by punctuation, spelling, dash style, editor wording, or platform truncation.

Tracking should use stable IDs first:

- Parent school joins: `school_uuid` / `school_selected_id`.
- Marketing reporting joins: `canonical_location_id` or `school_uuid`, depending on the reporting grain.
- Program joins: `program_id` when present, with `program_name` and aliases as labels.
- Event identity: `event_id`, never school ID or program ID.

## Verified Evidence

### Parent Form 4 And Helper Plugin

The parent Form 4 tracking contract uses these fields:

| Tracking field | Source | Status |
|---|---|---|
| `school_selected_id` | Gravity Forms `32.1` | Verified |
| `program_id` | Gravity Forms `32.2` | Verified |
| `days_per_week` | Gravity Forms `32.3` | Verified |
| `event_id` | Gravity Forms `32.4` | Verified |
| `school_selected_slug` | Gravity Forms `32.5` | Verified |
| `school_selected_name` | Gravity Forms `32.6` | Verified |
| `program_name` | Gravity Forms `32.7` | Verified |

The live tracking plugin reads these values for tracking and does not overwrite School Manager, Field 32, or KinderTales business delivery fields.

### CEFA Ops School Identity Map

The CEFA Ops reference `School Identity Map.md` states:

| Field | Meaning |
|---|---|
| `school_uuid` | Current KinderTales school unique ID and strongest working identity key |
| `location_name` | Working canonical school label |
| `region` | Province or operating-region label |
| `school_code` | BI team school/campus code |

This gives us a usable school-level source for tracking and reporting joins, but it does not include every external platform ID requested.

### BigQuery School Dimension

Verified with BigQuery under project `marketing-api-488017`:

| Table | Row count | Notes |
|---|---:|---|
| `mart_marketing.dim_school` | 53 | Populated school/location dimension |
| `cefa_core.dim_school` | 0 | Schema exists, currently empty |
| `cefa_core.dim_school_alias` | 0 | Schema exists, currently empty |
| `dataform_assertions.assert_dim_school_location_not_null` | 0 | Assertion/failure surface, not a populated master table |

`mart_marketing.dim_school` currently has:

| Column | Meaning for tracking |
|---|---|
| `school_id` | Same current values as `school_uuid` in sampled rows |
| `school_uuid` | Stable school ID used by parent forms and tracking |
| `canonical_location_id` | Marketing/reporting location ID |
| `location_code` | Marketing location code |
| `location_name` | Canonical school/location label |
| `school_slug` | URL/reporting slug |
| `timezone` | Reporting timezone |
| `landing_page_path` | School landing path |

Sample verified mapping from `mart_marketing.dim_school`:

| school_uuid | canonical_location_id | location_name | school_slug |
|---|---|---|---|
| `81236954-bcad-11ef-8bcb-028d36469a89` | `4abfc0c0-c672-43f6-899d-b3730f143db9` | Abbotsford - Highstreet | `abbotsford-highstreet` |
| `812376b1-bcad-11ef-8bcb-028d36469a89` | `5eca862e-d01f-4db9-965d-d91c956db45a` | Burlington - South Service Road | `burlington-south-service-road` |
| `81236ff4-bcad-11ef-8bcb-028d36469a89` | `burnaby-brentwood` | Burnaby - Brentwood | `burnaby-brentwood` |
| `81237055-bcad-11ef-8bcb-028d36469a89` | `burnaby-canada-way` | Burnaby - Canada Way | `burnaby-canada-way` |
| `812370b7-bcad-11ef-8bcb-028d36469a89` | `97938001-2850-4646-a0a7-bfb0bd12668d` | Burnaby - Kingsway | `burnaby-kingsway` |

### BigQuery Cross-System Indicators

BigQuery schema inspection found an assertion surface with these columns:

| Column | Status |
|---|---|
| `canonical_location_id` | Column exists in assertion surface |
| `school_name` | Column exists in assertion surface |
| `school_slug` | Column exists in assertion surface |
| `gbp_location_id` | Column exists in assertion surface |
| `greenrope_primary_location_id` | Column exists in assertion surface |
| `gravity_location_id` | Column exists in assertion surface |
| `piinpoint_school_key` | Column exists in assertion surface |

Important limitation: `dataform_assertions.assert_dim_school_location_not_null` has zero rows. In Dataform-style assertion tables, zero rows usually means no assertion failures, not that it is the source master table. This proves these fields exist in the modeling/QA surface, but it does not give us the populated crosswalk values.

### Paid Media Account Classification

BigQuery has account-level paid-media classification, not school-by-school ad naming.

Verified examples:

| Platform | Account ID | Account name | Reporting group | Status |
|---|---|---|---|---|
| Meta Ads | `1595846967472729` | CEFA Early Learning | Parents | Verified |
| Google Ads | `3820636025` | CEFA Franchisor | Franchise | Verified |
| Meta Ads | `505300888223754` | CEFA Franchisor | Franchise | Verified |
| Google Ads | `4159217891` | CEFA $3000 | Unclassified | Pending review |
| Meta Ads | `618283032704370` | CEFA Sullivan Heights | Parents location | Inferred |

This is useful for business-line containment, but it is not yet a canonical school-to-ad-naming table.

## Current Program Taxonomy Evidence

Recent parent `generate_lead` rows in GA4 BigQuery, filtered to `tracking_source=helper_plugin`, confirm these live Form 4 program values:

| program_id | program_name | Suggested canonical key | Suggested aliases |
|---|---|---|---|
| `411` | CEFA Baby | `baby` | Baby, CEFA Baby |
| `475` | Junior Kindergarten 1 | `jk1` | JK1, Junior Kindergarten 1 |
| `478` | Junior Kindergarten 2 | `jk2` | JK2, Junior Kindergarten 2 |
| `482` | Junior Kindergarten 3 | `jk3` | JK3, Junior Kindergarten 3 |
| `486` | CEFA Weekend Care Program | `weekend_care` | Weekend Care, CEFA Weekend Care, CEFA Weekend Care Program |
| `2030` | Waitlist | `waitlist` | Waitlist |

This is enough to start a canonical program table for tracking, but it is not yet enough to claim the CRM alias layer is complete. CRM/KinderTales journey-code aliases and capacity/waitlist automation labels still need confirmation from the downstream system or a source export.

## Recommended Canonical Tables

### `canonical_school_location`

Recommended columns:

| Column | Initial source | Status |
|---|---|---|
| `school_uuid` | CEFA Ops School Identity Map, Form 4 `32.1`, GA4 `school_selected_id` | Verified |
| `kindertales_school_id` | Same as `school_uuid` per CEFA Ops note, unless downstream proves separate ID | Working verified-as-same |
| `wordpress_school_manager_id` | WordPress School Manager post/object ID | Missing |
| `canonical_location_id` | `mart_marketing.dim_school` | Verified present; format mixed |
| `location_code` | `mart_marketing.dim_school` | Verified |
| `location_name` | `mart_marketing.dim_school`, CEFA Ops School Identity Map | Verified |
| `region` | CEFA Ops School Identity Map | Verified in Ops note |
| `school_code` | CEFA Ops School Identity Map | Verified in Ops note, with known blanks |
| `school_slug` | `mart_marketing.dim_school`, Form 4 `32.5`, GA4 `school_selected_slug` | Verified |
| `gravity_school_label` | Form 4 `32.6` / Gravity Forms entries | Partially verified |
| `ga4_location_label` | GA4 `school_selected_name` | Verified as event parameter, label normalization pending |
| `gbp_location_id` | GBP / warehouse upstream source | Missing from populated table |
| `gbp_location_name` | GBP / warehouse upstream source | Missing |
| `greenrope_primary_location_id` | CRM / warehouse upstream source | Missing from populated table |
| `gravity_location_id` | Gravity/source upstream | Missing from populated table |
| `piinpoint_school_key` | PiinPoint/source upstream | Missing from populated table |
| `ad_naming_location_key` | CEFA naming convention / paid-media source | Missing |
| `active_for_parent_tracking` | CEFA tracking governance | Needed |
| `is_test_location` | CEFA tracking governance | Needed |

### `canonical_program`

Recommended columns:

| Column | Initial source | Status |
|---|---|---|
| `program_id` | Form 4 `32.2`, GA4 `program_id` | Verified for observed values |
| `program_name` | Form 4 `32.7`, GA4 `program_name` | Verified for observed values |
| `program_key` | CEFA-defined normalized key | Proposed |
| `program_family` | CEFA-defined reporting group | Needed |
| `aliases` | Form labels, CRM labels, short labels | Partially proposed |
| `crm_program_id` | KinderTales/CRM source | Missing |
| `crm_journey_code` | KinderTales/CRM source | Missing |
| `active_for_parent_tracking` | CEFA tracking governance | Needed |

## Tracking Contract Recommendations

Use these in GTM, GA4, BigQuery, server-side tracking, and later CAPI/sGTM:

- Keep sending `school_selected_id` as the school UUID.
- Keep sending `school_selected_slug` and `school_selected_name` as readable metadata only.
- Keep sending `program_id` and `program_name` separately.
- Add a normalized `program_key` later if GTM or the helper plugin can derive it safely without touching business submission fields.
- Join school reporting on `school_uuid` or `canonical_location_id`, not school label.
- Join program reporting on `program_id`, not program label.
- Never use `school_uuid`, `school_slug`, `program_id`, or `program_name` as `event_id`.

## Open Questions Before Calling This Complete

1. Is `school_uuid` definitively the KinderTales school ID in every downstream environment, or does KinderTales also store a separate internal numeric/object ID?
2. What is the current WordPress School Manager internal ID for each school, if separate from the UUID emitted into Form 4?
3. Where is the populated source table/export that contains `gbp_location_id`, `greenrope_primary_location_id`, `gravity_location_id`, and `piinpoint_school_key`?
4. What exact GreenRope field should be used: group ID, location ID, tag ID, or another CRM-owned key?
5. Which ad naming key should become canonical for school-level parent campaigns: `school_code`, `location_code`, `school_slug`, or a separate NC1 token?
6. Are the current program IDs `411`, `475`, `478`, `482`, `486`, and `2030` stable School Manager/CRM IDs, or WordPress/GF option IDs that can change during future content updates?
7. What KinderTales journey-code values map to Baby, JK1, JK2, JK3, Weekend Care, and Waitlist?

## Immediate Next Steps

1. Create or expose a populated `canonical_school_location` table in BigQuery that starts from `mart_marketing.dim_school` and adds the missing CRM/GBP/ad-naming columns.
2. Create a small `canonical_program` seed table with the verified Form 4 program IDs and CEFA-defined aliases.
3. Confirm whether `school_uuid` and `kindertales_school_id` should be the same column or two columns.
4. Confirm the canonical school ad naming token with the CEFA naming convention owner before using it in automated platform joins.
5. Keep the helper plugin payload stable while the warehouse taxonomy catches up.

## Evidence Commands Used

```bash
CLOUDSDK_ACTIVE_CONFIG_NAME=cefa-bq-sticky bq --project_id=marketing-api-488017 query --use_legacy_sql=false
```

Tables and sources checked:

- `marketing-api-488017.mart_marketing.dim_school`
- `marketing-api-488017.cefa_core.dim_school`
- `marketing-api-488017.cefa_core.dim_school_alias`
- `marketing-api-488017.dataform_assertions.assert_dim_school_location_not_null`
- `marketing-api-488017.mart_marketing.account_scope_map`
- `marketing-api-488017.mart_marketing.paid_media_account_classification`
- `marketing-api-488017.analytics_267558140.events_*`
- `/Users/matthewbison/Vaults/CEFA Ops/70 - Reference/School Identity Map.md`
- `/Users/matthewbison/Vaults/CEFA Ops/70 - Reference/CRM & Systems Map.md`
- `/Users/matthewbison/Vaults/CEFA Ops/70 - Reference/School Inquiry Form URL Map.md`
