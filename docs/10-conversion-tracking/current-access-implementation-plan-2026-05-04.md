# Current Access Implementation Plan

Last updated: 2026-05-04

## Purpose

This file records what can now be done with the current Google access level for parent `cefa.ca`, Franchise Canada `franchise.cefa.ca`, and Franchise USA `www.franchisecefa.com`.

This is a planning document. No live GA4, GTM, or Google Ads configuration changes were made by this update.

## Current Access Summary

| Platform | Current access level | What this allows now | Remaining limitation |
|---|---|---|---|
| GA4 Admin API | Verified for all 3 CEFA properties | Read property settings, list custom dimensions, list/admin-check key events and links, prepare GA4 cleanup/change plans. | Write operations are possible by scope but should be performed only after approval. |
| GA4 Data API | Verified for all 3 CEFA properties | Query processed GA4 event data for parent, Franchise Canada, and Franchise USA. | GA4 reporting delay still applies; use BigQuery export where available for event-level parent checks. |
| GTM API | Verified account/container read for parent and franchise accounts | Audit containers, workspaces, tags, triggers, variables, versions, and destination mapping. | User-permission listing is blocked by missing `tagmanager.manage.users` scope. Container write/publish should be treated as approval-required even though edit/publish scopes are present. |
| Google Ads API | Verified read plus validate-only conversion-action mutate for parent and franchise accounts | Read conversion actions, confirm primary/secondary status, prepare validate-only changes before live mutate. | Live Ads mutations still require explicit user approval and a before/after table. |
| BigQuery | Verified query access | Query GA4 export, marts, rule registry, dashboard views, and reconciliation tables. | Parent/franchise business-truth marts are still stale after 2026-03-29 and need refresh/reconnect work. |
| Meta | Not yet fixed in this Google access pass | None from current Google auth. | Meta Events Manager/API access is still required for final Meta custom conversion and optimization-event signoff. |

## Verified Google Surfaces

### GA4

| Property | ID | Current access | Planned use |
|---|---:|---|---|
| Parent `Main Site - GA4` | `267558140` | Admin + Data API read verified | Parent helper event reporting, custom dimension/key-event audit, Ads-linked GA4 import review. |
| Franchise Canada `CEFA Franchise` | `259747921` | Admin + Data API read verified | Franchise Canada helper event reporting and custom dimension/key-event audit. |
| Franchise USA `CEFA Franchise - USA.` | `519783092` | Admin + Data API read verified | USA helper event reporting, currency review, custom dimension/key-event audit. |

### GTM

| Property | GTM account | Container | Current access | Planned use |
|---|---:|---|---|---|
| Parent | `4591216764` | `GTM-NZ6N7WNC` | Container read verified | Audit helper-event trigger, GA4 tag, Google Ads conversion tag, Meta tag, micro-event tags, and duplicate suppression. |
| Parent legacy | `4591216764` | `GTM-PPV9ZRZ` | Container read verified | Reference-only audit; do not restore as active final source. |
| Franchise Canada | `6004334435` | `GTM-TPJGHFS` | Container read verified | Audit helper/dispatch events, GA4, Google Ads, Meta, and LinkedIn destination mapping. |
| Franchise USA | `6004334435` | `GTM-5LZMHBZL` | Container read verified | Audit USA helper/dispatch events, GA4 mapping, and inactive/pending Ads/Meta final tags. |

### Google Ads

| Account | Customer ID | Current access | Planned use |
|---|---:|---|---|
| Manager `CEFA` | `6067148198` | Login customer verified | Manager context for Google Ads API reads and validate-only mutations. |
| Parent `CEFA $3000` | `4159217891` | Customer, conversion-action read, and validate-only conversion-action mutate verified | Parent conversion-action signoff and any approved primary/secondary cleanup. |
| Franchise `CEFA Franchisor` | `3820636025` | Customer, conversion-action read, and validate-only conversion-action mutate verified | Franchise Canada/USA conversion-action signoff and any approved primary/secondary cleanup. |

## What We Can Do Now

### Parent `cefa.ca`

| Step | Status | Action | Output |
|---|---|---|---|
| 1 | Ready | Audit `GTM-NZ6N7WNC` tags/triggers/variables for `school_inquiry_submit`, `generate_lead`, Google Ads, Meta, and micro-events. | Parent GTM mapping table with duplicate-risk notes. |
| 2 | Ready | Confirm whether Google Ads primary action `Inquiry Submit_ollo` is actually fired from the helper-event path. | Parent Ads action signoff: keep current primary, switch primary, or change trigger/tag. |
| 3 | Ready | Query GA4 Data API and BigQuery export for helper-plugin `generate_lead`, `validation_error`, and parameter coverage. | Parent GA4/BigQuery reconciliation table. |
| 4 | Ready | Use Google Ads API to report current conversion action status and recent conversion counts. | Parent Ads conversion-action report. |
| 5 | Approval required | If approved, adjust Google Ads primary/secondary or include-in-conversions settings using validate-only first, then live mutate. | Before/after Ads action change log. |
| 6 | Ready, non-Google gap remains | Document Meta requirements and wait for Meta access. | Meta access request / verification checklist. |

Parent decision to make:

- If `Inquiry Submit_ollo` is confirmed to fire only from the helper-event path, we can keep it as the parent primary Google Ads action.
- If it still fires from legacy thank-you/pageview or duplicate paths, we should not treat it as final until GTM is corrected.
- GA4-imported `generate_lead` currently exists as secondary/not included; it can remain secondary for reporting unless CEFA intentionally wants GA4 import as the bidding source.

### Franchise Canada `franchise.cefa.ca`

| Step | Status | Action | Output |
|---|---|---|---|
| 1 | Ready | Audit `GTM-TPJGHFS` Version 52 helper/dispatch mapping for `franchise_inquiry_submit` and `real_estate_site_submit`. | Franchise Canada GTM mapping table. |
| 2 | Ready | Confirm Google Ads conversion actions tied to Form 1 and Form 2: `fr_application_submit`, `fr_inquiry_submit`, and `fr_site_form_submit`. | Franchise Canada Ads action signoff. |
| 3 | Ready | Confirm whether current primary `fr_application_submit` is the right bidding signal or whether helper-event-specific actions should become primary. | Canada primary/secondary recommendation. |
| 4 | Ready | Query GA4 Data API for helper metadata and processed `generate_lead` rows. | Canada GA4 helper-event verification report. |
| 5 | Approval required | If approved, adjust Ads action primary/secondary settings after validate-only check. | Before/after Ads change log. |
| 6 | Pending Meta access | Confirm shared Meta dataset custom conversions and optimization event. | Canada Meta signoff once access exists. |

Canada decision to make:

- Current campaigns rely on existing franchise learning surfaces, so do not split/change the Meta dataset abruptly.
- For Google Ads, keep the current learning path unless the GTM audit proves it is not tied cleanly to confirmed helper events.

### Franchise USA `www.franchisecefa.com`

| Step | Status | Action | Output |
|---|---|---|---|
| 1 | Ready | Audit `GTM-5LZMHBZL` Version 15 helper/dispatch and GA4 mapping for USA forms. | USA GTM mapping table. |
| 2 | Ready | Confirm current USA Google Ads action `Application Submit (USA)` and hidden GA4-imported `generate_lead`. | USA Ads action signoff. |
| 3 | Ready | Query GA4 Data API for processed USA helper events and confirm whether browser evidence has reached reporting. | USA GA4 receipt report. |
| 4 | Ready | Review GA4 property currency `CAD` for `CEFA Franchise - USA.` and decide whether this is acceptable. | USA GA4 currency recommendation. |
| 5 | Approval required | If approved, activate or adjust USA Google Ads final helper-event mapping. | Before/after Ads/GTM change log. |
| 6 | Pending Meta access | Confirm whether USA should remain on shared Meta dataset temporarily or move to a separate USA dataset before serious optimization. | USA Meta transition decision. |

USA decision to make:

- USA should be separated more aggressively than Canada before serious production optimization, but do not change live Meta/Ads learning surfaces without an explicit transition plan.
- GA4 currency `CAD` should be reviewed because this property is USA-specific.

## Recommended Execution Order

| Order | Work | Reason |
|---:|---|---|
| 1 | Parent GTM and Ads conversion-action audit | Parent is closest to complete and is the immediate baseline for the rest of the system. |
| 2 | Parent full reconciliation: website event to GTM, GA4, Ads, BigQuery | Confirms the final path before cleanup or server-side work. |
| 3 | Franchise Canada GTM and Ads audit | Canada has active campaign learning and should be stabilized before any conversion-action changes. |
| 4 | Franchise USA GTM, GA4, and Ads audit | USA has separate-market needs and pending GA4/Ads/Meta final mapping decisions. |
| 5 | Meta access and Events Manager verification | Meta is the remaining major access gap across parent and franchise. |
| 6 | Business-truth refresh/reconciliation | GA4/Ads/Meta are not final inquiry truth until CRM/KinderTales/collector-backed data is current. |
| 7 | Approved cleanup/change batch | Only after signoff: archive obsolete GTM/GA4/Ads artifacts and make primary/secondary changes. |
| 8 | Phase 1B server-side work | Start collector/CAPI/MP audit/sGTM after browser + platform paths are stable. |

## Approval Gates

Do not perform these without explicit approval:

- Publish GTM versions.
- Change Google Ads primary/secondary status.
- Change Google Ads `include_in_conversions_metric`.
- Archive/remove GA4 custom definitions or key events.
- Archive/remove Ads conversion actions.
- Switch Meta datasets/pixels or custom conversion optimization events.
- Reactivate Gravity Forms Measurement Protocol as a final conversion source.

Safe without approval:

- Read/audit GA4, GTM, Google Ads, and BigQuery.
- Run Google Ads validate-only mutations.
- Produce signoff tables and recommendations.
- Update repo documentation.

## Remaining Access Gaps

| Gap | Priority | Needed |
|---|---:|---|
| Meta Events Manager/API | High | Access to parent and franchise datasets/pixels/custom conversions. |
| GTM user-permission admin visibility | Low | Add `tagmanager.manage.users` scope only if we need to inspect/manage user permissions. Not required for tag/container audits. |
| Production automation auth | Medium | Use workload identity or approved secrets management; do not rely on local user ADC for production automation. |
| Current business-truth source refresh | High | Refresh/reconnect parent inquiry and franchise lead-source marts after 2026-03-29. |

## Immediate Next Work Item

Start with a parent Google/GTM signoff:

1. Export/audit parent `GTM-NZ6N7WNC` tags, triggers, variables, and latest versions.
2. Confirm which Google Ads tag/action fires from `school_inquiry_submit`.
3. Compare that against Google Ads primary action `Inquiry Submit_ollo`.
4. Produce a recommendation: keep, retag, or switch action.
5. Do not change anything until approved.
