# ChatGPT Audit Prompt - CEFA Conversion Tracking Current Situation - 2026-05-05

Use this prompt when asking ChatGPT/GPT Pro to review the current CEFA conversion-tracking architecture and GitHub repo.

## Copy/Paste Prompt

I want you to audit our CEFA conversion-tracking setup and current plan. Please review the GitHub repo and challenge the plan if anything is risky, incomplete, duplicated, or not best practice.

Repository:

- `https://github.com/mert-atalay/conversion_tracking`
- Current working branch to review if available: `codex/franchise-canada-tracking-plan`

Primary docs to read first:

- `docs/10-conversion-tracking/README.md`
- `docs/10-conversion-tracking/parent-current-state-and-remaining-work-2026-05-04.md`
- `docs/10-conversion-tracking/parent-tag-assistant-preview-and-meta-restore-plan-2026-05-05.md`
- `docs/10-conversion-tracking/parent-analytics-tracking-skill-review-2026-05-05.md`
- `docs/10-conversion-tracking/franchise-ca-usa-tracking-status-2026-05-03.md`
- `docs/franchise-canada-phase1/README.md`
- `docs/franchise-usa-phase1/README.md`
- `docs/cross-property-measurement-boundaries.md`
- `docs/phase1b-measurement-protocol-server-side-options-2026-05-01.md`

Please treat the repo docs as the working source of truth, but also audit whether the plan is internally consistent.

## Important Clarification

There is one naming point that created confusion:

```text
Website/dataLayer source event for parent:
school_inquiry_submit

GA4 destination event:
generate_lead

Google Ads destination action:
Inquiry Submit_ollo

Meta destination event/custom conversion:
Inquiry Submit
```

So we are not using `Inquiry Submit` as the website/dataLayer event. `Inquiry Submit` is a Meta-side continuity label. The website source event remains `school_inquiry_submit`.

For franchise:

```text
Website/dataLayer source events:
franchise_inquiry_submit
real_estate_site_submit

GA4 destination event:
generate_lead

Meta destination event:
Lead or existing franchise continuity event/custom conversion depending on property
```

## What We Are Trying To Solve

We rebuilt tracking during the new website transition. The old setup had several problems:

- Too much reliance on thank-you pageviews and platform auto-detected events.
- Risk of duplicate conversions from Gravity Forms add-ons, GTM, and legacy tags.
- Parent and franchise tracking were mixed historically across datasets/accounts.
- The old parent GTM container had legacy click/application events that do not represent confirmed submissions.
- We need one clean website-side conversion event for each confirmed form submission, with a stable `event_id` and non-PII metadata.
- We want to preserve existing learning where practical, especially Google Ads and Meta conversion continuity, but not at the cost of bad duplicate sources.

The plan is:

- Website/plugin/WPCode emits neutral dataLayer source events.
- GTM maps those events to GA4, Google Ads, Meta, LinkedIn, and future destinations.
- Browser tracking is Phase 1.
- Measurement Protocol, CAPI, collector, and sGTM are Phase 1B/2 after browser parity is stable.
- Gravity Forms Measurement Protocol may be used only as an audit-only event first, not as a duplicate primary `generate_lead`.

## Parent `cefa.ca` Current Situation

Primary form:

- Gravity Forms Form `4`

Canonical website/dataLayer event:

- `school_inquiry_submit`

Current source implementation:

- CEFA-owned WordPress plugin: `cefa-conversion-tracking`
- Live plugin version documented: `0.4.3`
- Plugin emits the final dataLayer event only after confirmed Form 4 success.
- The plugin uses a one-time thank-you token so direct thank-you page visits/reloads do not create false conversions.

Parent payload uses Form 4 values:

- `32.1` = school UUID
- `32.2` = program ID
- `32.3` = days per week
- `32.4` = event ID
- `32.5` = school slug
- `32.6` = school name
- `32.7` = program name

Parent attribution fields:

- Fields `35` through `46` are used for UTM/click-ID/first-touch/last-touch handoff.
- These should not overwrite business delivery fields or KinderTales logic.

Parent GTM:

- Active container: `GTM-NZ6N7WNC`
- Old parent GTM `GTM-PPV9ZRZ` is archived/reference-only.

Parent destination mapping:

- `school_inquiry_submit` -> GA4 `generate_lead`
- `school_inquiry_submit` -> Google Ads existing action `Inquiry Submit_ollo`
- `school_inquiry_submit` -> Meta `Inquiry Submit` continuity event/custom conversion

Parent Google Ads:

- We intentionally kept the existing Google Ads action `Inquiry Submit_ollo` to preserve continuity/learning.
- The active label documented is `AW-802334988/cFt-CMrLufgCEIzSyv4C`.
- We are not trying to create a new Google Ads conversion action unless a migration is explicitly planned.

Parent GA4:

- GA4 property documented: `properties/267558140` / `Main Site - GA4`
- `generate_lead` is the destination/key event.
- Low-cardinality custom dimensions for the helper-plugin payload are documented as registered.
- BigQuery export previously showed helper-plugin `generate_lead` rows and no duplicate helper-plugin `generate_lead` event-ID groups in the checked window.

Parent Meta:

- Parent dataset/pixel currently documented: `918227085392601`
- Tag Assistant preview showed Meta Base Pixel and Meta `Inquiry Submit` working when reopened.
- Public live GTM version `9` still has parent Meta Tags `39` and `40` paused after an emergency mitigation.
- The next planned GTM action is a narrow Meta-only restore: reopen only Tags `39` and `40`.

Critical parent incident/problem:

- We previously had GTM Custom HTML tags for GA4 micro-events (`form_start`, `form_submit_click`, `validation_error`) that called `gtag()` using the same event name that triggered the tag.
- This created a loop/repeated inline script risk and may have caused page freezing/form instability.
- Those unsafe tags are documented as Tags `66`, `67`, and `68`.
- They must stay paused.
- If GA4 micro-events are restored later, they should use native GA4 Event tags or another non-recursive pattern, not Custom HTML `gtag()` snippets.

Parent open items:

- Publish only Meta Tags `39` and `40`; keep Tags `66`, `67`, and `68` paused.
- Run controlled desktop and mobile Form 4 submissions after publish.
- Confirm one `school_inquiry_submit`.
- Confirm GA4 `generate_lead`.
- Confirm Google Ads `AW-802334988/cFt-CMrLufgCEIzSyv4C`.
- Confirm Meta `Inquiry Submit` with matching final `event_id`.
- Confirm Contact Us and inquiry dropdowns no longer freeze.
- Confirm no repeated inline `G-T65G018LYB` scripts.
- Reconcile GTM, GA4, Google Ads, Meta, BigQuery, Gravity Forms, and KinderTales/business truth after the next traffic window.

## Franchise Canada Current Situation

Live URL:

- `https://franchise.cefa.ca`

Important domain caution:

- This is a subdomain under `cefa.ca`, so GTM and cookie/linker behavior must be hostname-scoped carefully.

Forms:

- Gravity Forms Form `1` / Franchise Inquiry
- Gravity Forms Form `2` / Submit a Site / Real Estate Site
- Gravity Forms Form `3` / Newsletter

Website source implementation:

- WPCode bridge currently emits confirmed-success helper events.
- GAConnector remains in place and is intentionally kept for now.
- A patch backfills missing/placeholder GAConnector attribution fields into Gravity Forms hidden fields before save.
- `gclid` has a cleanup rule: current `_gcl_aw` wins over stale GAConnector value when available.

Canonical website/dataLayer events:

- Form `1`: `franchise_inquiry_submit`
- Form `2`: `real_estate_site_submit`

Destination mapping:

- GTM maps helper events/dispatch events to GA4, Google Ads, Meta, and LinkedIn destinations.

Canada GTM:

- Current container documented: `GTM-TPJGHFS`
- Current evidence says it contains `franchise_inquiry_submit`, `real_estate_site_submit`, `cefa_franchise_inquiry_dispatch`, and `cefa_real_estate_site_dispatch`.

Canada GA4:

- Property documented: `259747921` / `CEFA Franchise`
- Processed reports have shown at least one helper-plugin `generate_lead` row with franchise Canada metadata.
- Some rows still appeared with `(not set)` metadata, so reporting still needs follow-up.

Canada Google Ads:

- Account documented: `3820636025` / `CEFA Franchisor`
- Current evidence shows `fr_application_submit` primary while `generate_lead (GA4)`, `fr_site_form_submit`, and `fr_inquiry_submit` are secondary.
- A media-owner decision is still needed before changing primary/bidding status.

Canada Meta:

- Canada may temporarily stay on the shared/parent dataset `918227085392601` if active franchise campaigns rely on that dataset for learning.
- Target architecture still prefers separation eventually.
- Direct Events Manager custom-conversion confirmation is pending.

Canada open items:

- Re-run processed GA4 reports after the patched submissions process.
- Confirm Canada Meta custom conversions in Events Manager.
- Decide Google Ads primary/secondary conversion action with media owner.
- Keep hostname/container boundaries strict because `franchise.cefa.ca` is under `cefa.ca`.

## Franchise USA Current Situation

Live URLs:

- `https://franchisecefa.com`
- `https://www.franchisecefa.com`

Forms:

- Gravity Forms Form `1` / Franchise Inquiry
- Gravity Forms Form `2` / Submit a Site

Website source implementation:

- WPCode fallback bridge emits confirmed-success helper events.
- GAConnector remains in place.
- A patch backfills missing GAConnector fields from cookies before Gravity Forms saves Form 1/Form 2 entries.

Canonical website/dataLayer events:

- Form `1`: `franchise_inquiry_submit`
- Form `2`: `real_estate_site_submit`

USA GTM:

- Container documented: `GTM-5LZMHBZL`
- GTM Version `18` documented as live: `CEFA Franchise USA Meta Lead reliability fix - 2026-05-04`
- Version `18` keeps helper-event/GA4 mapping, USA Meta dataset split, old click/micro cleanup, and Meta `fbq` init fallback.

USA GA4:

- GA4 property documented: `519783092` / `CEFA Franchise - USA.`
- Base collection is working.
- Browser-level GA4 hit evidence exists for Form 2.
- Processed GA4 `generate_lead` reports still need recheck after processing delay.
- Property default currency is documented as `CAD`; open question whether it should be `USD`.

USA Google Ads:

- GA4 property is linked to Google Ads customers `3820636025` and `4159217891`.
- USA-related conversion actions exist in both accounts.
- The observed USA actions still had zero all-conversion volume in checked reporting.
- The correct USA bidding account/action still needs media-owner confirmation before adding/activating final Google Ads helper-event tags.

USA Meta:

- USA is now separated to dataset/pixel `1531247935333023`.
- Old shared dataset `918227085392601` was removed from active USA WordPress header/body options.
- Runtime checks documented `1531247935333023` and zero active public-runtime occurrences of `918227085392601`.
- Meta custom conversion created: `1915200622465036` / `USA Franchise Lead`.
- The custom conversion uses standard Meta `Lead` plus URL path containing `inquiry-thank-you`, scoped to USA dataset `1531247935333023`.
- Events Manager receipt confirmation is still pending.

USA open items:

- Confirm Meta Events Manager live `Lead` receipt on dataset `1531247935333023`.
- Confirm if Form 2/Site Submit needs its own USA Meta custom conversion or remains reporting-only.
- Confirm USA Google Ads account and primary conversion action.
- Re-run processed GA4 Data API reports for helper `generate_lead`.
- Decide whether USA GA4 currency should be `USD`.
- Disable or prove audit-only any active USA Gravity Forms Google Analytics feed that could duplicate final `generate_lead`.

## Measurement Protocol / Server-Side Direction

Current position:

- Do not use Gravity Forms Measurement Protocol to send a second primary GA4 `generate_lead` while browser/GTM `generate_lead` is active.
- If tested, use audit-only events first:
  - Parent: `school_inquiry_submit_server_audit`
  - Franchise USA example: `franchise_us_inquiry_submit_server_audit`
- Audit events should not be key events.
- Audit events should not be imported into Google Ads.
- Audit events should share the same form `event_id`.
- Audit events should send only approved non-PII metadata and attribution fields.

Longer-term preferred direction:

```text
Gravity Forms confirmed submission
-> CEFA plugin/webhook/collector
-> validation + durable persistence
-> queue
-> GA4 Measurement Protocol / Meta CAPI / Google Ads offline or enhanced conversions / BigQuery / sGTM
```

The collector/server-side layer is for attribution strength and business truth, not a reason to duplicate browser conversions immediately.

## Specific Review Questions For You

Please audit and answer:

1. Is the parent source/destination naming model correct?
   - Website event: `school_inquiry_submit`
   - GA4: `generate_lead`
   - Google Ads: existing `Inquiry Submit_ollo`
   - Meta: `Inquiry Submit`

2. Do you agree that `Inquiry Submit` should remain only a Meta/destination continuity label and not become the dataLayer event?

3. Do you agree that parent Tags `66`, `67`, and `68` should stay paused because Custom HTML `gtag()` micro-events can self-trigger/loop?

4. Is the narrow parent Meta-only restore plan safe?
   - Reopen only Tags `39` and `40`
   - Keep `66`, `67`, `68` paused
   - Run controlled desktop/mobile QA

5. Should parent Meta use custom `Inquiry Submit`, standard `Lead`, or both?
   - Consider continuity/learning, CAPI future, and Meta best practice.

6. Should Google Ads continue using the existing `Inquiry Submit_ollo` action for now?
   - We want to preserve learning and not create a new conversion action unnecessarily.

7. Are the parent micro-events correctly treated as reporting/remarketing only, not bidding events?

8. Is the Gravity Forms Measurement Protocol audit-only stance correct?
   - Or should we use Measurement Protocol sooner in another way without duplicating GA4 `generate_lead`?

9. For Franchise Canada, is it acceptable to temporarily keep the shared Meta dataset if active campaigns depend on it?
   - What is the safest migration plan to a separated franchise Canada dataset without losing learning?

10. For Franchise USA, is the separate dataset/pixel `1531247935333023` the correct direction?
   - Should USA use standard Meta `Lead`, a custom conversion, or both?

11. For USA Google Ads, what is the safest way to choose between linked accounts/actions before enabling final helper-event Ads tags?

12. Do you see any duplicate-source risk from Gravity Forms Google Analytics feeds, old GTM tags, GAConnector, or WPCode bridge logic?

13. Are there any GA4 custom dimension/cardinality risks in the current payload plan?
   - We currently avoid registering `event_id`, full URLs, raw referrers, click IDs, and PII as custom dimensions.

14. Does the plan correctly separate:
   - parent enrollment leads,
   - Canada franchise leads,
   - USA franchise leads,
   - real estate/site submissions?

15. What should be the exact next implementation order before ads are used aggressively?

## Current Working Recommendation To Challenge

Our current internal recommendation is:

1. Parent: keep plugin source event `school_inquiry_submit`.
2. Parent: publish only Meta Tags `39` and `40`; keep unsafe GA4 Custom HTML tags paused.
3. Parent: confirm desktop/mobile Form 4 QA across GA4, Google Ads, Meta, and BigQuery.
4. Parent: do not accept Google Ads auto-suggested click/application conversions as primary conversions.
5. Parent: keep Google Ads continuity on existing `Inquiry Submit_ollo`.
6. Parent: keep Meta continuity on `Inquiry Submit`, but verify whether adding/using standard `Lead` is better for future CAPI.
7. Franchise Canada: keep current shared Meta dataset temporarily if campaigns depend on it, but use strict `site_context`, `business_unit`, `market`, `lead_type`, `form_family`, and custom conversions.
8. Franchise USA: continue separated dataset/pixel `1531247935333023`.
9. Franchise USA: confirm Events Manager receipt and Google Ads primary action before serious optimization.
10. All properties: do not activate Gravity Forms Measurement Protocol as a second primary `generate_lead`; use it only as audit-only until parity is proven.
11. All properties: no PII to GA4/GTM/Ads/Meta event parameters.
12. All properties: business truth should eventually be validated through Gravity Forms/CRM/KinderTales/Synuma/SiteZeus/collector/BigQuery, not browser tags alone.

Please give:

- A concise risk ranking.
- Any corrections to the event taxonomy.
- Any changes you would make to the GTM/GA4/Ads/Meta plan.
- Any duplicate-risk warnings.
- A recommended next-action checklist.
- Any questions that must be answered before making live platform changes.
