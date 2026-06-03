# GreenRope Current-State Aggregate Corrections

Last updated: 2026-05-04

## Purpose

Record the follow-up review and correction of the GreenRope BigQuery aggregate and dashboard views after a second-agent review flagged risky metric names and sparse join behavior.

This is a BigQuery/data workstream note. It does not redefine final business lead truth, paid-media truth, or CRM source-system ownership.

## Scope

| Field | Value |
|---|---|
| Workstream | BigQuery and reporting data |
| Project | `marketing-api-488017` |
| Verification date | 2026-05-04 |
| Live BigQuery writes made | Yes: replaced two views only |
| Physical table writes made | No |
| GreenRope writes made | No |
| Live ad platform / tracking writes made | No |

## Reviewer Assessment

`Verified`: The review was directionally correct.

The current BigQuery object is a GreenRope opportunity current-state aggregate. It is not final CRM lead truth, not completed-tour truth, not enrollment truth, and not paid-media truth.

The physical table columns remain as first-load legacy names for compatibility, but dashboard-facing views now expose clearer semantic names.

## Live View Corrections

| View | Status | Change |
|---|---|---|
| `mart_marketing.vw_greenrope_school_funnel_school_daily` | Verified updated | Added `opportunity_created_date`, `snapshot_as_of_date`, `opportunities_created`, `current_inquiry_phase_opportunities`, `ad_attributed_current_inquiry_phase_opportunities`, `current_tour_phase_opportunities`, and `current_enrollment_phase_opportunities`. School-level metric columns are populated only for dashboard-safe one-school mappings. |
| `mart_marketing.vw_school_marketing_dashboard_with_crm_daily` | Verified updated | Added explicit zero-fill and reason fields: `greenrope_join_reason`, `greenrope_metrics_zero_filled`, `greenrope_max_opportunity_created_date`, and current-state metric aliases. Legacy dashboard columns remain for compatibility. |

The physical fact table was not renamed because downstream views and dashboard code may depend on existing column names. Treat these as legacy physical names:

| Legacy physical field | Dashboard-safe semantic meaning |
|---|---|
| `snapshot_date` | `opportunity_created_date` |
| `raw_opportunity_count` | `opportunities_created` |
| `inquiries_total` | `current_inquiry_phase_opportunities` |
| `paid_inquiries` | `ad_attributed_current_inquiry_phase_opportunities` |
| `non_paid_inquiries` | `no_detected_ad_attribution_current_inquiry_phase_opportunities` |
| `tour_phase_count` | `current_tour_phase_opportunities` |
| `enrollment_phase_count` | `current_enrollment_phase_opportunities` |

## Verified Aggregate State

| Check | Result |
|---|---:|
| Fact rows | 6,390 |
| Distinct `snapshot_date` / opportunity-created dates | 253 |
| Distinct GreenRope groups | 52 |
| Raw opportunities counted | 24,916 |
| Date range | 2025-06-12 through 2026-05-03 |
| Current inquiry-phase opportunities | 15,352 |
| Ad-attributed current inquiry-phase opportunities | 2,898 |
| No-detected-ad-attribution current inquiry-phase opportunities | 12,454 |
| Current tour-phase opportunities | 840 |
| Current enrollment-phase opportunities | 904 |
| Missing created-date count | 0 |
| Rows where paid + non-paid does not equal inquiry total | 0 |

## Dashboard Join State

`Verified`: The dashboard base view is a school-date spine from 2025-09-17 through 2026-05-02 with 12,084 rows.

The GreenRope fact table is newer and wider than the dashboard base window: it runs from 2025-06-12 through 2026-05-03.

Current `vw_school_marketing_dashboard_with_crm_daily` row reasons:

| `greenrope_join_reason` | Rows | Meaning |
|---|---:|---|
| `greenrope_metrics_available` | 6,144 | Safe mapping and a GreenRope group/date aggregate exists. |
| `safe_mapping_no_opportunities_for_created_date` | 5,484 | Safe mapping exists, but there were no opportunities created for that school/group/date; metrics are zero-filled. |
| `duplicate_greenrope_group_mapping` | 456 | GreenRope group maps to multiple schools; school-level metrics remain null to avoid double counting. |
| `no_greenrope_group_mapping` | 0 | No current school rows lack a GreenRope bridge mapping. |

Dashboard-safe totals in `vw_school_marketing_dashboard_with_crm_daily` for its current date window:

| Metric | Value |
|---|---:|
| `greenrope_opportunities_created` | 24,508 |
| `greenrope_current_inquiry_phase_opportunities` | 15,298 |
| `greenrope_ad_attributed_current_inquiry_phase_opportunities` | 2,876 |
| `greenrope_current_tour_phase_opportunities` | 817 |
| `greenrope_current_enrollment_phase_opportunities` | 879 |

The dashboard reader service account successfully queried the updated dashboard view after the view replacement.

## Group 50 Mapping Issue

`Partial`: GreenRope group `50` maps to both `South Surrey - Morgan Crossing` and `South Surrey - Morgan Crossing East`.

The group has real source data in the fact table:

| Metric | Group `50` value |
|---|---:|
| Raw opportunities | 141 |
| Current inquiry-phase opportunities | 34 |
| Ad-attributed current inquiry-phase opportunities | 16 |
| Current tour-phase opportunities | 23 |
| Current enrollment-phase opportunities | 25 |

Current handling:

- Dashboard-safe school metrics remain null for both mapped South Surrey rows.
- The source group data remains available in `fct_greenrope_school_funnel_daily`.
- Do not split, duplicate, or allocate group `50` to either school without a business/source-system decision.

## Missing Warehouse Evidence

`Pending`: The following tables are still required before the GreenRope definitions can be called fully governed:

| Missing surface | Why it is required |
|---|---|
| Raw or restricted GreenRope opportunities table | Lets the warehouse audit exact source phase strings, custom fields, and date fields used by the extractor. |
| Normalized GreenRope opportunity table | Provides a stable, PII-aware source for current-state and historical CRM metrics. |
| GreenRope field dictionary snapshot | Verifies the custom-field names behind UTM/click-ID matching. |
| GreenRope phase taxonomy snapshot | Verifies phase labels instead of relying only on extractor hard-coded strings. |
| GreenRope phase path snapshot | Provides funnel/path context for phase-state interpretation. |

## Cost Snapshot

| Usage area | Current value |
|---|---:|
| May 2026 query usage after this verification | 13.8818 GiB |
| Share of 1 TiB monthly free query tier | About 1.356 percent |
| May 2026 query job count | 469 |

This remained well inside the free query tier.

## Next Actions

| Priority | Status | Action |
|---:|---|---|
| 1 | Pending | Resolve GreenRope group `50` before using South Surrey school-level CRM metrics. |
| 2 | Pending | Load or snapshot `GetOpportunityFieldsRequest`, `GetPhasesRequest`, and `GetPhasePathsRequest`. |
| 3 | Pending | Design restricted raw/stage GreenRope opportunity tables with PII controls. |
| 4 | Pending | Automate the daily GreenRope aggregate refresh after field/phase governance is clear. |
| 5 | Pending | Decide whether to rename physical fact-table columns in a migration, or keep compatibility names and rely on view aliases. |

## Source Evidence

- Verified with live BigQuery queries in `marketing-api-488017` on 2026-05-04.
- Live BigQuery writes were limited to `CREATE OR REPLACE VIEW` for the two views listed above.
- No raw GreenRope payloads, contacts, emails, phone numbers, notes, or secrets were written to this repo.
