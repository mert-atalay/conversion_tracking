# GPT Pro Audit Response And Plan Adjustments - 2026-05-05

Status: reviewed and accepted as a planning refinement. No live GTM, GA4, Google Ads, Meta, WordPress, or plugin changes were made by this documentation update.

## Executive Decision

The second-opinion audit does not change the core CEFA plan.

Keep the current parent source/destination model:

| Layer | Name |
|---|---|
| Parent website/dataLayer source event | `school_inquiry_submit` |
| GA4 destination event | `generate_lead` |
| Google Ads destination action | `Inquiry Submit_ollo` |
| Meta destination continuity event | `Inquiry Submit` |

The strongest accepted refinements are:

- Lock `GTM-NZ6N7WNC` as the active parent container and keep `GTM-PPV9ZRZ` reference-only.
- Do not import or merge old enhanced GTM JSON exports into the live parent container as-is.
- Keep parent Tags `66`, `67`, and `68` paused until rebuilt with native/non-recursive GA4 event tags.
- Preserve Google Ads continuity on `Inquiry Submit_ollo`, but audit that no equivalent GA4-imported `generate_lead` is also primary for the same parent lead.
- Keep Meta `Inquiry Submit` for continuity now; investigate a controlled future migration to standard Meta `Lead` plus custom conversions.
- Add school-intent reporting fields after the current browser path is stable, especially `campaign_school_slug`, selected/landing school separation, and match status.

## What Changed In The Plan

### 1. Container Drift Is Now A Top Risk

Current parent truth remains:

- Active parent container: `GTM-NZ6N7WNC`
- Old parent container: `GTM-PPV9ZRZ`, archived/reference-only

Accepted guardrail:

- Do not import old `GTM-PPV9ZRZ` exports, old enhanced JSON files, or old thank-you/pageview-style logic into the active parent container without a line-by-line migration review.
- If old assets are used, treat them only as reference material for IDs, labels, or historical context.

Reason:

- Current docs already state the live parent path is `GTM-NZ6N7WNC`.
- Older docs and exports may still name `GTM-PPV9ZRZ` as main website GTM.
- Mixing those lineages risks reintroducing old thank-you-page triggers, old click/application conversions, and duplicate conversion sources.

### 2. School Parameters Help Reporting, Not Bidding By Themselves

Accepted clarification:

- School/program/day parameters improve QA, reporting, custom conversions, audience building, BigQuery joins, and future offline/server-side work.
- They do not strongly teach Google or Meta bidding by themselves unless they influence the optimized conversion goal, conversion value, custom conversion rule, or offline/CRM-quality feedback.

Implication:

- Do not overclaim that sending school metadata alone solves school-funded campaign optimization.
- The long-term learning layer is CRM/offline-quality feedback: inquiry, qualified lead, tour booked, enrollment, and actual enrolled school.

### 3. School-Intent Fields Become A Next-Phase Requirement

Current parent plugin already emits:

- `school_selected_slug`
- `school_landing_slug`
- `school_match_status`

Accepted future addition:

- `campaign_school_slug`
- `landing_school_slug` or mapped equivalent from `school_landing_slug`
- `selected_school_slug` or mapped equivalent from `school_selected_slug`
- `school_match_status`
- `lead_quality_value`, only if value-based bidding is explicitly approved

Implementation rule:

- Do not rename the live payload immediately if GTM/GA4/Ads/Meta already depend on `school_selected_slug` and `school_landing_slug`.
- Prefer adding alias variables in GTM/BigQuery/docs first, then decide whether the plugin should emit normalized aliases in a later version.
- `campaign_school_slug` should come from controlled campaign URL parameters or naming rules, not only page parsing.

Recommended campaign parameter:

```text
utm_school=<school-slug>
```

or:

```text
campaign_school_slug=<school-slug>
```

### 4. Meta Parent Event Strategy Is Now A Deliberate Migration Question

Current parent recommendation remains:

- Keep Meta `Inquiry Submit` now for continuity.
- Restore only parent Meta Tags `39` and `40`.
- Do not double-fire both `Inquiry Submit` and `Lead` as active production optimization events without a migration plan.

Accepted future direction:

- Investigate moving parent Meta to standard `Lead` as the underlying event.
- Use custom conversions and parameters to segment parent inquiry, school/program/day, and market.
- Migrate only after confirming current campaigns/custom conversions that depend on `Inquiry Submit`.

Reason:

- Standard `Lead` is cleaner for Meta-native optimization and CAPI.
- Abruptly replacing `Inquiry Submit` could disrupt existing event continuity and learning.

### 5. Google Ads Primary Conversion Ownership Needs An Explicit Audit

Current parent recommendation remains:

- Keep existing `Inquiry Submit_ollo`.
- Keep label `AW-802334988/cFt-CMrLufgCEIzSyv4C`.
- Do not create a new parent primary conversion action unless deliberately migrating.

Accepted added check:

- Verify whether GA4 `generate_lead` is imported into Google Ads.
- If imported, verify whether it is primary or secondary.
- Ensure only one equivalent parent lead action is primary for bidding.

Rule:

- Direct Google Ads `Inquiry Submit_ollo` can stay primary.
- Equivalent GA4-imported `generate_lead` should be secondary unless CEFA intentionally changes the bidding model.

## Risk Ranking Accepted

| Risk | Severity | Accepted control |
|---|---|---|
| Duplicate primary `generate_lead` or lead actions | Critical | Browser/GTM remains primary; MP audit-only; one equivalent Google Ads parent action primary. |
| Recursive GA4 Custom HTML tags | Critical | Keep Tags `66`, `67`, `68` paused; rebuild with native GA4 Event tags if needed. |
| Parent GTM container drift | Critical | Active `GTM-NZ6N7WNC`; old `GTM-PPV9ZRZ` reference-only; no old JSON imports as-is. |
| Parent Google Ads double-primary | High | Audit direct Ads action vs GA4 import primary/secondary status. |
| Cross-property mixing | High | Parent/franchise/USA/site-submit stay separated by event contract, hostname, dataset, and conversion-goal discipline. |
| Parent Meta `Inquiry Submit` vs standard `Lead` | Medium | Keep continuity now; plan controlled migration later. |
| Franchise Canada shared Meta dataset | Medium | Temporary continuity exception only if active campaigns depend on it. |
| USA Google Ads action/account ambiguity | Medium | Confirm media-owner account/action before final Ads helper tags. |
| GA4 cardinality/PII | Medium | Register only bounded business fields; no PII/click IDs/full URLs/event IDs as GA4 custom dimensions. |

## Current Parent Next Action Remains

1. Confirm active parent GTM production container is still `GTM-NZ6N7WNC`.
2. Publish only parent Meta Tags `39` and `40`.
3. Keep Tags `66`, `67`, and `68` paused.
4. Run desktop Form 4 QA.
5. Run mobile Form 4 QA.
6. Confirm exactly one `school_inquiry_submit`.
7. Confirm GA4 `generate_lead`.
8. Confirm Google Ads `AW-802334988/cFt-CMrLufgCEIzSyv4C`.
9. Confirm Meta `Inquiry Submit` with matching final `event_id`.
10. Confirm no Contact Us / inquiry dropdown freeze.
11. Confirm no repeated inline `G-T65G018LYB` scripts.
12. Audit duplicate sources: Gravity Forms GA feeds, MP, old GTM, hardcoded pixels, auto-detected Google conversions.
13. Audit Google Ads primary/secondary status for `Inquiry Submit_ollo` and GA4-imported `generate_lead`.
14. Reconcile browser, GA4, Ads, Meta, BigQuery, Gravity Forms, and CRM/KinderTales after the next traffic window.

## Follow-Up GPT Prompt

Use this only if we want GPT Pro to investigate the remaining strategic/platform questions in more depth.

```text
Please review the CEFA conversion-tracking repo again with a narrow focus on four unresolved architecture decisions:

Repo: https://github.com/mert-atalay/conversion_tracking
Branch: codex/franchise-canada-tracking-plan

Read first:
- docs/10-conversion-tracking/gpt-pro-audit-response-plan-adjustments-2026-05-05.md
- docs/10-conversion-tracking/parent-current-state-and-remaining-work-2026-05-04.md
- docs/10-conversion-tracking/parent-tag-assistant-preview-and-meta-restore-plan-2026-05-05.md
- docs/10-conversion-tracking/franchise-ca-usa-tracking-status-2026-05-03.md
- docs/cross-property-measurement-boundaries.md
- docs/phase1b-measurement-protocol-server-side-options-2026-05-01.md

Questions:

1. Parent Meta migration:
Should parent stay on custom Meta event `Inquiry Submit`, migrate to standard Meta `Lead`, or run a staged transition? Please propose the safest migration sequence that avoids double-counting and preserves current learning.

2. Parent Google Ads primary action:
If the direct Google Ads action `Inquiry Submit_ollo` is already primary and GA4 `generate_lead` is also imported, what should be primary vs secondary? Please give an exact decision tree.

3. School-funded campaign learning:
How should we model `campaign_school_slug`, `school_selected_slug`, `school_landing_slug`, and `school_match_status` so franchise-funded school campaigns can report matched vs mismatched leads without suppressing parent choice or reducing form volume? When, if ever, should `lead_quality_value` be used for bidding?

4. Server-side roadmap:
When should CEFA add Gravity Forms Measurement Protocol audit events, Meta CAPI, Google Ads enhanced/offline conversions, and sGTM? Please propose a phased rollout that prevents duplicate primary conversions.

Please return:
- risk ranking,
- exact recommended event/parameter names,
- what to keep unchanged now,
- what to test next,
- what not to do,
- and any live platform checks required before implementation.
```

## Final Plan After This Review

Proceed with the current internal recommendation, with the refinements above.

The helper plugin remains the correct parent source. The main operational risks are old-container drift, duplicate conversion sources, recursive GTM tags, unclear primary bidding actions, and unmanaged Meta event migration.
