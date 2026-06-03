# GreenRope Metric Definitions And API Map

Last updated: 2026-05-04

## Purpose

Define every GreenRope metric currently loaded into BigQuery for CEFA dashboards, including the GreenRope API endpoint, source object, source fields, view aliases, and interpretation limits.

This document is intentionally narrow. It defines GreenRope-backed dashboard metrics; it does not define Google Ads, Meta, GA4, naming-convention, or final conversion-tracking business truth.

## Scope

| Field | Value |
|---|---|
| Workstream | BigQuery and reporting data |
| Source system | GreenRope / CRM+ |
| BigQuery aggregate table | `marketing-api-488017.mart_marketing.fct_greenrope_school_funnel_daily` |
| BigQuery school bridge | `marketing-api-488017.mart_marketing.bridge_greenrope_group_school` |
| Dashboard view | `marketing-api-488017.mart_marketing.vw_school_marketing_dashboard_with_crm_daily` |
| Source API endpoint used for current aggregate | `GetOpportunitiesRequest` by `group_id` |
| Verification date | 2026-05-04 |
| Live writes made | BigQuery view/docs update only; no physical fact-table, GreenRope, ad platform, or tracking writes |

## Important Dashboard Label Rule

`Verified`: The current GreenRope aggregate is a current-state opportunity aggregate. It contains ad-attribution evidence, not solid paid-media truth.

Use this label:

```text
GreenRope ad-attributed current inquiry-phase opportunities
```

Do not use this label:

```text
GreenRope paid inquiries
```

Reason:

- The source is GreenRope opportunity custom fields, not Google Ads, Meta, or spend reconciliation.
- The count means a current inquiry-phase GreenRope opportunity had at least one UTM/click-id marker.
- It does not prove that the inquiry was billed, optimized, imported, or confirmed by an ad platform.

The physical first-load table column is `paid_inquiries`, but the dashboard view exposes the safer semantic field `greenrope_ad_attributed_current_inquiry_phase_opportunities`. Legacy dashboard aliases remain for compatibility only.

## Current Loaded Endpoints

| Endpoint | Status | What it provides | Current BigQuery use |
|---|---|---|---|
| `GetGroupsRequest` | Verified support input | GreenRope group IDs and names | Used to confirm group names for the school bridge. |
| `GetOpportunitiesRequest account_id=... group_id=... response=json` | Verified metric source | Opportunity rows by GreenRope group, including current phase, created date, and custom fields | Used to build the current GreenRope daily current-state aggregate. |

## Current Metric Definitions

Use the semantic view fields for new dashboard work. The physical table fields are legacy first-load names kept for compatibility.

| Dashboard / view metric | Physical table field | Status | GreenRope endpoint | Source object / fields | Definition |
|---|---|---|---|---|---|
| `greenrope_group_id` | `greenrope_group_id` | Verified | `GetGroupsRequest`; `GetOpportunitiesRequest` request parameter | GreenRope group ID | CRM group used as the extraction and school-mapping key. |
| `greenrope_group_name` | `greenrope_group_name` | Partial | `GetGroupsRequest` | Group `name` / `groupname` | Human-readable GreenRope group name. Useful for QA, not the canonical CEFA school key. |
| `greenrope_opportunity_created_date` / `opportunity_created_date` | `snapshot_date` | Verified legacy physical name | `GetOpportunitiesRequest` | Opportunity `datetimecreated`, fallback candidates `created_at`, `datecreated`, `datemodified` | Opportunity created-date bucket. This is not a true warehouse snapshot date. The current load found 0 missing created-date rows. |
| `greenrope_max_opportunity_created_date` | Derived from `snapshot_date` | Verified | BigQuery fact table | Max loaded opportunity-created date | Latest loaded GreenRope opportunity-created date available to the dashboard view. |
| `snapshot_as_of_date` | Derived from `api_fetched_at` | Verified | Local extraction metadata | Extraction timestamp | Date the API extraction was fetched. This is closer to a real snapshot/as-of date than the physical `snapshot_date` field. |
| `greenrope_opportunities_created` / `opportunities_created` | `raw_opportunity_count` | Verified extraction count | `GetOpportunitiesRequest` | Opportunity rows returned for the group/date | Count of GreenRope opportunity rows with a usable created date for that group/date. This is not deduped lead truth. |
| `greenrope_current_inquiry_phase_opportunities` | `inquiries_total` | Partial | `GetOpportunitiesRequest` | Opportunity `phase` / `stage` / `status` | Count of dated opportunity rows currently in `inquiry`, `future inquiries`, or `future inquiry` phases, bucketed by opportunity created date. This is current phase-state evidence, not total CRM leads. |
| `greenrope_ad_attributed_current_inquiry_phase_opportunities` | `paid_inquiries` | Partial | `GetOpportunitiesRequest` | Opportunity custom fields | Count of current inquiry-phase rows where at least one normalized custom field is populated for `utmsource`, `utmmedium`, `utmcampaign`, `gclid`, `gbraid`, `wbraid`, `fbclid`, or `msclkid`. This is ad-attribution evidence only. |
| `greenrope_no_detected_ad_attribution_current_inquiry_phase_opportunities` | `non_paid_inquiries` | Partial | `GetOpportunitiesRequest` | Opportunity custom fields | Count of current inquiry-phase rows where none of the current UTM/click-id markers were detected. This does not prove the lead was organic; it only means the checked fields were empty/missing. |
| `greenrope_current_tour_phase_opportunities` | `tour_phase_count` | Partial | `GetOpportunitiesRequest` | Opportunity `phase` / `stage` / `status` | Count of rows currently in a tour-like phase, bucketed by opportunity created date. This is not completed-tour or scheduled-tour history. |
| `greenrope_current_enrollment_phase_opportunities` | `enrollment_phase_count` | Partial | `GetOpportunitiesRequest` | Opportunity `phase` / `stage` / `status` | Count of rows currently in enrollment/won-like phase, bucketed by opportunity created date. This is not a final operational enrollment ledger. |
| `missing_created_date_count` | `missing_created_date_count` | Verified for current extraction | `GetOpportunitiesRequest` | Opportunity date fields listed above | Count of opportunity rows that did not have a usable date in the current extractor. Current extraction result was 0. |
| `api_fetched_at` | `api_fetched_at` | Verified | Local extraction metadata | Extraction timestamp | Time the GreenRope API data was fetched. |
| `loaded_at` | `loaded_at` | Verified | BigQuery load metadata | Load timestamp | Time the aggregate row was prepared for BigQuery load. |
| `extraction_status` | `extraction_status` | Verified | Local extraction metadata | Extraction result | Current successful rows are marked `Verified`; this means the extraction query succeeded, not that every metric is final business truth. |
| `warning_count` | `warning_count` | Verified | Local extraction metadata | Extraction warnings | Number of extraction warnings attached to the row. |
| `warnings` | `warnings` | Verified | Local extraction metadata | Extraction warnings | Warning text, if present. |
| `greenrope_join_reason` | Derived in dashboard view | Verified | BigQuery bridge and fact table | Join/mapping state | Explains whether GreenRope metrics are available, zero-filled for no opportunities, withheld for duplicate group mapping, missing a group mapping, or outside loaded GreenRope dates. |
| `greenrope_metrics_zero_filled` | Derived in dashboard view | Verified | BigQuery bridge and fact table | Join/mapping state | `true` only when the school has a safe GreenRope mapping and no aggregate row exists for that created-date bucket, so dashboard metrics are explicitly zero-filled. |

## School Mapping Definitions

| Dashboard / bridge field | Status | Endpoint / source | Definition |
|---|---|---|---|
| `greenrope_group_id` | Verified | `GetGroupsRequest` plus local GreenRope group map | GreenRope group used to join daily CRM counts to CEFA schools. |
| `canonical_location_id` | Partial | `mart_marketing.dim_school` plus local group map | Current warehouse location ID. Mixed UUID/slug formats still exist in the warehouse. |
| `school_id` / `school_uuid` | Verified for current warehouse row | `mart_marketing.dim_school` | Current school join key used by the dashboard mart. |
| `location_code` / `location_name` | Verified for current warehouse row | `mart_marketing.dim_school` | Human-readable school/location fields. |
| `mapping_status` | Partial | Local mapping logic | `unique_group_to_school` when one GreenRope group maps to one school row; `duplicate_group_to_multiple_schools` when one CRM group maps to multiple school rows. |
| `is_dashboard_safe_school_mapping` / `greenrope_dashboard_safe_mapping` | Partial | Local mapping logic | `true` only when the CRM group has a one-school mapping. Dashboard totals should not add duplicate CRM group rows as school-level truth. |

Known duplicate:

| GreenRope group | Status | Current handling |
|---|---|---|
| `50` | Partial | Maps to both `South Surrey - Morgan Crossing` and `South Surrey - Morgan Crossing East`; marked not dashboard-safe for automatic school-level totals. |

## Endpoint Capability Map

These endpoints exist in the current GreenRope capability notes, but only `GetGroupsRequest` and `GetOpportunitiesRequest` feed the current BigQuery aggregate.

| Endpoint | Current use in BigQuery | Metric family | Status / interpretation |
|---|---|---|---|
| `GetGroupsRequest` | Yes | Mapping | Group ID/name support. |
| `GetOpportunitiesRequest` | Yes | Current inquiry-phase, ad-attributed current inquiry-phase, current tour-phase, current enrollment-phase opportunity counts | Primary current-state CRM opportunity aggregate source. |
| `GetOpportunityFieldsRequest` | No | Field dictionary | Useful for validating custom-field names; not currently loaded into BigQuery. |
| `GetPhasesRequest` | No | Phase taxonomy | Should be used in future to validate phase labels instead of relying only on hard-coded phase strings. |
| `GetPhasePathsRequest` | No | Phase path taxonomy | Useful for CRM funnel taxonomy diagnostics; not currently dashboard source. |
| `GetCRMActivitiesRequest` | No | Operational activities | Activity/workflow evidence only; not canonical lead/tour/enrollment totals. |
| `GetCRMActivityTypesRequest` | No | Activity taxonomy | Useful for diagnostics; not currently dashboard source. |
| `GetContactsRequest group_id=...` | No | Contact population / enrichment | Not loaded into BigQuery because it may contain PII. |
| `GetCRMActivitiesEmailsRequest contact_id=...` | No | Email engagement | Not loaded into BigQuery. |
| `GetAllCRMActivitiesEmailsRequest group_id=...` | No | Email engagement | Not loaded into BigQuery. |
| `GetEventsRequest` / event-related endpoints | No | Event/tour context | Secondary context only; current notes say event-to-opportunity linkage is weaker than opportunity phase. |
| `GetJourneysRequest group_id=...` | No | Journey catalog | Catalog/definition context only. |
| `GetAllJourneysRequest group_id=... contact_id=...` | No | Journey progress | Not loaded into BigQuery because it is contact-level evidence. |
| `GetWebsiteConversionsRequest` | No | Website conversion evidence | Current GreenRope notes say this returned zero rows in tested groups and should not be trusted as production source yet. |

## Current Dashboard Guidance

Use these fields in dashboard labels:

| Dashboard label | Field |
|---|---|
| GreenRope opportunities created | `greenrope_opportunities_created` |
| GreenRope current inquiry-phase opportunities | `greenrope_current_inquiry_phase_opportunities` |
| GreenRope ad-attributed current inquiry-phase opportunities | `greenrope_ad_attributed_current_inquiry_phase_opportunities` |
| GreenRope current inquiry-phase opportunities without detected ad attribution | `greenrope_no_detected_ad_attribution_current_inquiry_phase_opportunities` |
| GreenRope current tour-phase opportunities | `greenrope_current_tour_phase_opportunities` |
| GreenRope current enrollment-phase opportunities | `greenrope_current_enrollment_phase_opportunities` |
| GreenRope join reason | `greenrope_join_reason` |
| GreenRope metrics zero-filled | `greenrope_metrics_zero_filled` |

Legacy compatibility fields still exposed by the dashboard view:

| Legacy field | Prefer instead |
|---|---|
| `greenrope_inquiries_total` | `greenrope_current_inquiry_phase_opportunities` |
| `greenrope_ad_attributed_inquiries` | `greenrope_ad_attributed_current_inquiry_phase_opportunities` |
| `greenrope_no_detected_ad_attribution_inquiries` | `greenrope_no_detected_ad_attribution_current_inquiry_phase_opportunities` |
| `greenrope_tour_phase_count` | `greenrope_current_tour_phase_opportunities` |
| `greenrope_enrollment_phase_count` | `greenrope_current_enrollment_phase_opportunities` |

Avoid these labels:

| Avoid label | Reason |
|---|---|
| Paid inquiries | Too strong; current source is UTM/click-id evidence in GreenRope, not ad-platform payment or conversion reconciliation. |
| Organic inquiries | Too strong; lack of detected ad attribution does not prove organic source. |
| Total CRM leads | Too strong; current metric counts only opportunities currently in inquiry-like phases. |
| Completed tours | Too strong; current source is opportunity current phase, not attended-tour event history. |
| Tours scheduled today | Too strong; current tour-phase count is bucketed by opportunity created date, not tour scheduled date. |
| Enrollments final | Too strong; current source is opportunity current phase, not the final operational enrollment ledger. |

Use `greenrope_join_reason` before treating a dashboard value as zero or missing. Safe one-school mappings with no GreenRope row are explicitly zero-filled; duplicate group mappings stay null to avoid double counting.

## Current Gaps

| Gap | Status | Owner workstream | Notes |
|---|---|---|---|
| Raw or restricted GreenRope opportunities table | Pending | BigQuery and CRM/source systems | Needed to audit exact source phase strings, custom fields, and date fields without depending only on extractor logic. |
| Normalized GreenRope opportunity table | Pending | BigQuery and CRM/source systems | Needed for stable, PII-aware opportunity-level current-state and historical metrics. |
| GreenRope field dictionary in BigQuery | Pending | BigQuery and CRM/source systems | `GetOpportunityFieldsRequest` should be loaded or snapshotted before treating custom-field matching as fully governed. |
| GreenRope phase taxonomy in BigQuery | Pending | BigQuery and CRM/source systems | `GetPhasesRequest` and `GetPhasePathsRequest` should be loaded or snapshotted to make phase definitions auditable. |
| Ad-attributed inquiry naming cleanup | Partial | BigQuery | Dashboard views now expose `greenrope_ad_attributed_current_inquiry_phase_opportunities`, but the physical first-load table column remains `paid_inquiries`; treat it as a legacy physical name. |
| Physical fact-table naming migration | Open question | BigQuery | The physical table was not renamed on 2026-05-04 to avoid breaking downstream users. Decide later whether to migrate or rely on view aliases. |
| Daily refresh automation | Pending | BigQuery | The current GreenRope aggregate was manually loaded. |

## Source Evidence

- Current aggregate load and dashboard view verification were performed against BigQuery project `marketing-api-488017` on 2026-05-03 and 2026-05-04.
- The 2026-05-04 correction note is `docs/20-bigquery/greenrope-current-state-aggregate-corrections-2026-05-04.md`.
- Endpoint and logic references come from local CEFA GreenRope code and CRM capability notes in `/Users/matthewbison/Desktop/agentic-brain/`.
- No GreenRope secrets, raw contacts, emails, phone numbers, CRM notes, or raw opportunity payloads are stored in this repo document.
