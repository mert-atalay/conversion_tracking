# GPT Pro Review Handoff - Parent Tracking State, Franchise Transition, and Meta Dataset Question

Last updated: 2026-04-28

## Purpose

This document is a complete handoff for a second-pass GPT Pro review before we move from the completed parent-side staging work into franchise conversion tracking.

The main review question is no longer whether parent Form 4 tracking can work. That has been implemented and tested on staging.

The main strategic question now is how to handle franchise tracking, especially Meta dataset separation, without unnecessarily damaging live campaign learning.

## Executive Summary

We started with a concern that the new CEFA parent website did not expose a reliable browser-side conversion structure. The agency initially suggested using the Gravity Forms Google Analytics Add-On and/or thank-you-page signals. After testing, that was not enough for our desired tracking contract because it did not guarantee one clean confirmed-success event, matching event IDs between browser and Gravity Forms, and clean separate school/program/day metadata.

We built and deployed a narrow CEFA-owned WordPress helper plugin called `CEFA Conversion Tracking`. It does not replace Gravity Forms, the CEFA School Manager, Field 32 UI, school selection, program/day rendering, KinderTales, GTM, GA4, Google Ads, Meta, CAPI, collector, or sGTM. It only owns the tracking bridge.

Current parent staging result:

- One confirmed successful Form 4 submission produces one `school_inquiry_submit` dataLayer event.
- Browser `event_id` matches Gravity Forms field `32.4`.
- School/program/day values are clean separate fields from Form 4 field `32.*`.
- Attribution fields are persisted in hidden fields `35` through `46`.
- GTM maps the helper-plugin event to GA4 `generate_lead` and supporting destination tags.
- GA4 custom dimensions were created in the parent `Main Site - GA4` property.

The next workstream is franchise conversion tracking.

Important current complication:

- `franchise.cefa.ca` is a subdomain under `cefa.ca`, so GTM updates must be carefully contained by hostname.
- The agency reportedly set parent, Canada franchise, and USA franchise Meta events under the same Meta dataset/pixel.
- Current Canada franchise Meta campaigns rely on that shared dataset, so immediate separation could lose or weaken campaign learning.
- The existing plan says parent, franchise Canada, and franchise USA should ultimately have separate Meta datasets or pixels.
- We need guidance on the safest transition path.

## Repositories And Working Surfaces

Primary GitHub repo for the helper plugin and operational docs:

- `https://github.com/mert-atalay/conversion_tracking.git`

Local repo path:

- `/Users/matthewbison/Desktop/cefa-nexus/conversion_tracking`

Canonical CEFA tracking knowledge base:

- `/Users/matthewbison/Desktop/cefa-nexus/CEFA/cefa conversion tracking/`

Important plugin files:

- `cefa-conversion-tracking.php`
- `assets/js/cefa-conversion-tracking.js`
- `includes/class-cefa-conversion-tracking.php`
- `includes/class-cefa-conversion-tracking-event-id.php`
- `includes/class-cefa-conversion-tracking-confirmation-payload.php`
- `includes/class-cefa-conversion-tracking-datalayer-payload.php`
- `includes/class-cefa-conversion-tracking-attribution.php`
- `includes/class-cefa-conversion-tracking-duplicate-guard.php`
- `includes/class-cefa-conversion-tracking-rest-controller.php`

Important operational docs now in the GitHub repo:

- `docs/parent-production-cutover-checklist.md`
- `docs/cross-property-measurement-boundaries.md`
- `docs/phase1a/README.md`
- `docs/phase1a/datalayer-contract.md`
- `docs/phase1a/event-flow-and-lifecycle.md`
- `docs/phase1a/guardrails.md`
- `docs/phase1a/acceptance-tests.md`
- `docs/phase1a/plugin-vs-theme-decision.md`
- `docs/phase1a/gravity-forms-add-on-decision.md`

## Parent Website Current State

Parent staging site:

- `https://cefamain.kinsta.cloud`

Current staging inquiry route:

- `/submit-an-inquiry-today/?location=<school-slug>`

Canonical website-side success event:

- `school_inquiry_submit`

GA4 destination event:

- `generate_lead`

Current parent staging GTM container:

- Public ID: `GTM-NZ6N7WNC`

Current parent GA4 property:

- Account: `accounts/17532283`
- Account name in UI: `CEFA`
- Property: `properties/267558140`
- Property name: `Main Site - GA4`
- UI breadcrumb: `CEFA > cefa.ca > Main Site - GA4`

Current parent plugin:

- Plugin name: `CEFA Conversion Tracking`
- Version: `0.3.0`

Current important parent event contract:

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: "school_inquiry_submit",
  event_id: "<same as Form 4 field 32.4>",
  form_id: "4",
  form_family: "parent_inquiry",
  lead_type: "cefa_lead",
  lead_intent: "inquire_now",
  school_selected_id: "<32.1>",
  school_selected_slug: "<32.5>",
  school_selected_name: "<32.6>",
  program_id: "<32.2>",
  program_name: "<32.7>",
  days_per_week: "<32.3>",
  utm_source: "<35>",
  utm_medium: "<36>",
  utm_campaign: "<37>",
  utm_term: "<38>",
  utm_content: "<39>",
  gclid: "<40>",
  gbraid: "<41>",
  wbraid: "<42>",
  fbclid: "<43>",
  msclkid: "<44>",
  first_landing_page: "<45>",
  first_referrer: "<46>",
  inquiry_success: true,
  inquiry_success_url: window.location.href,
  page_context: "parent",
  tracking_source: "helper_plugin"
});
```

## Parent Form Field Map

Form 4 Field 32 subfields:

| Field | Meaning |
| --- | --- |
| `32.1` | selected school UUID |
| `32.2` | selected program ID |
| `32.3` | selected days per week |
| `32.4` | unique event ID |
| `32.5` | school slug |
| `32.6` | school name |
| `32.7` | program name |

Form 4 attribution fields:

| Field | Meaning |
| --- | --- |
| `35` | `utm_source` |
| `36` | `utm_medium` |
| `37` | `utm_campaign` |
| `38` | `utm_term` |
| `39` | `utm_content` |
| `40` | `gclid` |
| `41` | `gbraid` |
| `42` | `wbraid` |
| `43` | `fbclid` |
| `44` | `msclkid` |
| `45` | first landing page |
| `46` | first referrer |

Fields `33` and `34` are intentionally not modified by the plugin because the redesign uses them for location/location-title values.

## Parent GA4 Admin Configuration

The following event-scoped custom dimensions were created in `Main Site - GA4` / property `267558140`:

- `form_id`
- `form_family`
- `lead_type`
- `lead_intent`
- `school_selected_id`
- `school_selected_slug`
- `school_selected_name`
- `program_id`
- `program_name`
- `days_per_week`
- `tracking_source`
- `page_type`
- `cta_id`
- `cta_location`

Existing GA4 key events in the same property:

- `generate_lead`
- `inquiry_click`
- `email_click`
- `phone_click`
- `find_a_school_click`
- `purchase`

Nothing was deleted from GA4.

High-cardinality or implementation-specific values were intentionally not registered as standard GA4 custom dimensions:

- `event_id`
- `gclid`
- `gbraid`
- `wbraid`
- `fbclid`
- `msclkid`
- full landing URLs
- full referrers

Reason:

- They are useful for payloads, debugging, backend matching, BigQuery, Meta CAPI, and server-side tracking, but not ideal as standard GA4 reporting dimensions.

## Parent GTM And Destination State

Current staging GTM uses the helper-plugin event as the final source.

Important rule:

- The final lead source is `school_inquiry_submit`, not a thank-you pageview and not a Gravity Forms Google Analytics Add-On event.

GTM maps:

- `school_inquiry_submit` -> GA4 `generate_lead`
- `school_inquiry_submit` -> Google Ads parent inquiry conversion once final label is confirmed
- `school_inquiry_submit` -> Meta event once final Meta strategy is confirmed

Micro-conversion events currently supported:

- `parent_inquiry_cta_click`
- `find_a_school_click`
- `phone_click`
- `email_click`
- `form_start`
- `form_submit_click`
- `validation_error`

Current recommendation:

- Micro-conversions should be GA4/reporting diagnostics at launch.
- They should stay out of Google Ads bidding unless explicitly approved.

## Why The Plan Changed

Initial concern:

- Agency confirmed there was no standardized data attribute convention and no clear custom dataLayer success event.
- They suggested thank-you URL parameters and the Gravity Forms Google Analytics Add-On.

What we tested:

- The Gravity Forms Google Analytics Add-On could fire a basic GA/GTM event.
- However, the add-on did not give enough control for the required contract.
- Earlier testing showed risk of collapsed complex-field values, mismatched event IDs, and duplicate event sources.

Current accepted approach:

- Use a narrow CEFA-owned helper plugin for tracking only.
- Keep Gravity Forms, School Manager, Field 32, school/program/day UI, and KinderTales/business delivery untouched.
- Use GTM as the mapping layer, not as the source of business truth.

This is a hybrid boundary:

- Agency/theme/School Manager owns business behavior and visible form UX.
- Helper plugin owns tracking identity, attribution persistence, confirmed-success event, and duplicate guards.
- GTM maps the neutral website event to destinations.
- GA4, Ads, Meta, CAPI, sGTM, and BigQuery remain destination or later-phase systems.

## Current Production Cutover Plan For Parent

Before moving parent staging to production:

- Confirm final production parent domain and route paths.
- Confirm final inquiry route replacing staging `/submit-an-inquiry-today/`.
- Confirm final thank-you route and query behavior.
- Confirm Form 4 remains the parent inquiry form.
- Confirm Field 32 subfields remain stable.
- Confirm attribution fields `35` through `46` remain stable.
- Confirm `school_inquiry_submit` fires only after confirmed Form 4 success.
- Confirm browser `event_id` matches Gravity Forms field `32.4`.
- Confirm direct thank-you visits and reloads do not fire false conversions.
- Confirm invalid Form 4 submissions do not fire `school_inquiry_submit`.
- Confirm GTM maps `school_inquiry_submit` to GA4 `generate_lead`.
- Confirm GTM passes registered GA4 parameters.
- Confirm production Google Ads conversion action and label.
- Confirm parent Meta dataset/pixel and final event name.
- Confirm micro-conversions stay out of bidding unless explicitly approved.

After parent production is stable:

- Review old GA4 custom dimensions and archive only if no longer needed.
- Review old GA4 key events and remove key-event status only if no longer needed.
- Archive old GTM tags/triggers/variables that are proven obsolete.
- Begin next-phase server-side collector, Meta CAPI, sGTM, and BigQuery work.

## Long-Term Roadmap

Current phase:

- Browser-side Phase 1A for parent tracking is effectively complete on staging.

Next near-term phase:

- Parent production cutover.
- Franchise Canada tracking audit and implementation.
- Franchise USA tracking audit and implementation after Canada.

Later strengthening phases:

- Server-side collector.
- Meta CAPI using shared `event_id`.
- sGTM on a custom domain.
- BigQuery persistence and reporting marts.
- Broader server-side routing and lifecycle upload strategy.

Important constraint:

- sGTM and CAPI are not needed to validate the parent staging browser contract.
- They are for attribution strengthening and recovery from browser-side loss.

## Cross-Property Tracking Plan

The current CEFA plan says the three surfaces should be separated:

| Surface | Business role | URL/domain | Rollout order |
| --- | --- | --- | --- |
| Parent Canada | Parent school inquiry funnel | `cefa.ca` | 1 |
| Franchise Canada | Canada franchise B2B funnel | `franchise.cefa.ca` | 2 |
| Franchise USA | USA franchise B2B funnel | `www.franchisecefa.com` | 3 |

Boundary principle:

- Parent enrollment leads and franchise development leads are different business funnels.
- They should not share the same conversion taxonomy as if they were the same outcome.
- Shared code or shared infrastructure is acceptable, but event names, destination mappings, and reporting boundaries should remain property-specific.

Current plan says:

- Separate GA4 property for parent.
- Separate GA4 property for franchise Canada.
- Separate GA4 property for franchise USA.
- Ultimately, separate Meta datasets or pixels for parent, franchise Canada, and franchise USA.

## Franchise Canada Subdomain Risk

Canada franchise site:

- `franchise.cefa.ca`

This is a subdomain under `cefa.ca`, so GTM changes need extra caution.

Risks:

- Parent all-pages tags could accidentally fire on the franchise subdomain.
- Franchise tags could accidentally fire on parent pages.
- First-party cookie domain behavior could bleed between `cefa.ca` and `franchise.cefa.ca`.
- Cross-domain/linker settings could behave differently than expected.
- Shared Meta pixel/dataset can blur parent and franchise funnel diagnostics.

Required GTM safeguards:

- Use hostname filters on every major tag group.
- Parent tags should fire only on parent hostnames.
- Franchise Canada tags should fire only on `franchise.cefa.ca`.
- Avoid broad all-pages triggers unless they are explicitly scoped.
- Audit linker/cross-domain settings before publishing.
- Audit cookie domain assumptions before porting parent attribution logic.

Recommended event direction:

- Parent submit: `school_inquiry_submit`.
- Franchise Canada submit: use a franchise-specific website event such as `franchise_inquiry_submit`.
- Franchise USA submit: use a franchise-specific website event too, but destination mappings must be separate from Canada.

## Meta Dataset Situation

Reported current state:

- Agency has set parent, franchise Canada, and franchise USA under the same Meta dataset/pixel.
- Franchise Canada campaigns currently rely on this shared dataset.
- Ads Manager accounts may be separate, but the dataset/pixel is shared.
- USA is also reportedly using the same dataset, which is especially risky.

Current concern:

- If we split Meta datasets abruptly, we may lose or weaken the existing Meta learning for active franchise campaigns.
- This is the user’s main question and should be treated seriously.

Current recommendation before GPT Pro review:

- Do not immediately move Canada franchise live campaigns away from the shared dataset if they currently rely on it.
- Keep the shared dataset temporarily for learning continuity.
- Add strict event separation inside the current shared dataset.
- Use Meta custom conversions or event rules to separate parent vs franchise reporting.
- Prepare a future separate franchise Canada dataset and migrate gradually only after testing.
- Separate USA more aggressively because it is a different country, different domain, different market, and likely different optimization/reporting needs.

## What To Configure In Current Shared Meta Dataset Now

For Canada franchise, because live campaigns rely on the current shared dataset:

1. Keep the current shared Meta dataset temporarily.
2. Add clean franchise-specific event parameters.
3. Create separate Meta custom conversions for franchise Canada.
4. Do not abruptly switch live campaign optimization.
5. Build/test a separate franchise dataset in parallel before migration.

Recommended Meta event parameters for franchise events:

```js
{
  site_context: "franchise_ca",
  business_unit: "franchise",
  market: "canada",
  lead_type: "franchise_lead",
  form_family: "franchise_inquiry",
  page_type: "<page type>",
  cta_id: "<cta id>",
  cta_location: "<cta location>",
  event_id: "<unique event ID>",
  event_source: "website",
  tracking_source: "gtm_or_helper_plugin"
}
```

Recommended custom conversions inside the shared dataset:

- `Franchise Canada Lead`
- `Parent Inquiry Lead`
- optional `Franchise Canada CTA Click`

Rules should use:

- URL/host condition such as `event_source_url contains franchise.cefa.ca`
- and/or `site_context equals franchise_ca`
- plus the final lead event condition

This allows separate reporting and transition prep without immediately breaking current learning.

## Why Not Keep Shared Meta Dataset Forever

Reasons to eventually separate:

- Parent and franchise campaigns optimize toward different lead types.
- Parent enrollment leads and franchise development leads are different quality signals.
- Shared datasets make audience quality harder to interpret.
- Shared datasets make diagnostics harder when both funnels use similar event names like `Lead`.
- CAPI/server-side dedup becomes more complicated if unrelated funnels share event names and event IDs.
- USA should have cleaner isolation because it is a different domain, market, and sales motion.

Reasons not to separate immediately:

- Current franchise Meta campaigns rely on the existing shared dataset.
- Meta campaign learning may weaken if optimization is moved abruptly.
- A new dataset may need time to collect enough clean events for stable optimization.
- Campaign history and existing event ranking/custom conversions may be tied to current setup.

The likely best path is phased migration, not instant replacement.

## Proposed Meta Transition Model

Phase A - Stabilize current shared dataset:

- Keep current shared dataset for active campaigns.
- Add host-based GTM containment.
- Add `site_context`, `business_unit`, `market`, and `lead_type` parameters.
- Create custom conversions for parent and franchise Canada inside the shared dataset.
- Confirm live events can be segmented cleanly.

Phase B - Prepare separated datasets:

- Create or identify separate franchise Canada dataset/pixel.
- Create or identify separate franchise USA dataset/pixel.
- Configure test events and QA.
- Keep production optimization unchanged while testing.

Phase C - Gradual migration:

- Move new franchise campaigns or duplicated test campaigns to the separated dataset first.
- Avoid editing all active campaigns at once.
- Compare event volume, match quality, cost per lead, lead quality, and attribution behavior.
- Move live optimization only once the new dataset has enough reliable signal.

Phase D - Final separation:

- Parent remains on parent dataset.
- Franchise Canada uses franchise Canada dataset.
- Franchise USA uses franchise USA dataset.
- Shared historical dataset remains available for old reporting, but not as the clean future architecture.

## What We Need To Audit For Franchise Next

Franchise Canada:

- Live GTM container and all tags/triggers/variables.
- Hostname scoping.
- Current Meta pixel/dataset ID.
- Current Meta event names used by campaigns.
- Which campaigns optimize to which events/custom conversions.
- Current GA4 property and event names.
- Current Google Ads conversion actions.
- Forms, CTAs, thank-you pages, scheduling flows, or CRM handoff.
- Whether the site uses Gravity Forms or another form stack.
- Whether the existing parent helper plugin pattern should be adapted or whether a separate franchise helper is cleaner.

Franchise USA:

- Same audit as Canada, but with stronger default assumption that USA needs separate Meta dataset/pixel.
- Confirm final domain and GTM container.
- Confirm whether USA campaigns currently optimize against the shared dataset and how much live learning is at risk.

## Questions For GPT Pro

Please review the current state and answer these directly.

1. Is the current parent implementation boundary correct?

We are using a narrow WordPress helper plugin for tracking identity, attribution capture, duplicate guards, and one confirmed-success dataLayer event, while leaving Gravity Forms, School Manager, and business delivery untouched. Is this still the right boundary?

2. Is our parent production cutover plan missing anything?

We have plugin event identity, GTM mapping, GA4 custom dimensions, micro-events, attribution fields, duplicate/false-positive guards, and production QA scenarios. What, if anything, should be added before production?

3. For `franchise.cefa.ca`, what is the safest GTM containment pattern?

Because it is a subdomain under `cefa.ca`, should we use strict hostname triggers on every tag, separate containers, separate environment variables, or another pattern?

4. Should franchise Canada and parent Canada share the same Meta dataset temporarily?

Current franchise campaigns rely on the shared dataset. We believe immediate separation could lose or weaken Meta learning. Is the transition model above the best path, or would you separate immediately despite the learning risk?

5. How real is the Meta learning-loss risk?

Please explicitly assess the risk that moving Canada franchise campaigns from the shared dataset to a new dataset/pixel will reset or weaken optimization. How should we minimize that risk?

6. Should franchise Canada ultimately have a separate dataset from parent?

Our plan says yes because parent enrollment and franchise development are different conversion signals. Do you agree, or is there a case for keeping Canada parent and franchise in one dataset with strict custom conversions?

7. Should USA franchise be separated immediately?

Our current view is yes. USA has a different domain, market, sales motion, and likely reporting/compliance needs. Is there any reason not to separate USA dataset/pixel before serious production optimization?

8. What event taxonomy should franchise use?

Should franchise submit use `franchise_inquiry_submit`, `franchise_lead_submit`, `generate_lead` directly, or another neutral site event mapped in GTM to platform events?

9. How should Meta event names be handled during transition?

Should we keep the old Meta event name for continuity and add parameters/custom conversions, or move to standard `Lead` with franchise-specific parameters?

10. What is the best campaign migration strategy?

If current campaigns optimize to the old shared dataset event, should we duplicate campaigns/ad sets for testing, switch custom conversions gradually, or keep existing campaigns unchanged until the new dataset has volume?

11. What should happen with CAPI?

When we add Meta CAPI, should CAPI go first to the current shared dataset for continuity, or should it wait until the separate parent/franchise datasets are ready?

12. What should happen with sGTM?

The current plan defers sGTM until after browser parity and plugin tracking are stable. Is that still correct for franchise, or does franchise separation make sGTM more urgent?

13. Should the helper plugin be extended for franchise?

Should the existing `CEFA Conversion Tracking` plugin become configurable by site context and support franchise forms, or should franchise get a separate helper plugin to avoid coupling parent and franchise logic?

14. What custom parameters are essential for franchise Meta events?

We proposed `site_context`, `business_unit`, `market`, `lead_type`, `form_family`, `page_type`, `cta_id`, `cta_location`, `event_id`, and `tracking_source`. Are these enough? What should be added or removed?

15. What are the non-negotiable QA tests before changing live franchise campaigns?

Please list the minimum browser, GTM, GA4, Meta Events Manager, and campaign-level checks before moving any active franchise campaign optimization.

## Current Working Recommendation Before GPT Pro Review

Parent:

- Continue with the helper-plugin-to-GTM model.
- Do not delete old GA4/GTM configuration until production cutover is complete.
- Keep micro-conversions out of bidding at launch.

Franchise Canada:

- Do not immediately split live campaigns away from the shared Meta dataset.
- First add GTM hostname containment and clean franchise parameters.
- Create franchise-specific custom conversions inside the shared dataset.
- Prepare separate franchise Canada dataset in parallel.
- Migrate gradually only after clean event volume and learning risk are understood.

Franchise USA:

- Strongly prefer separate Meta dataset/pixel before serious optimization.
- Audit current USA dependency on shared dataset before changing live campaigns.

Overall:

- The future architecture should be separated by business funnel.
- The transition should avoid unnecessary learning loss.
- The final plan should not let platform learning concerns permanently block clean measurement boundaries.
