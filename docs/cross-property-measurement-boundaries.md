# Cross-Property Measurement Boundaries

Last updated: 2026-04-28

This document keeps parent, franchise Canada, and franchise USA tracking decisions separated while allowing shared implementation patterns.

## Properties

| Surface | Business role | URL/domain | Rollout order |
| --- | --- | --- | --- |
| Parent Canada | Parent school inquiry funnel | `cefa.ca` | 1 |
| Franchise Canada | Canada franchise B2B funnel | `franchise.cefa.ca` | 2 |
| Franchise USA | USA franchise B2B funnel | `www.franchisecefa.com` | 3 |

## Boundary Decisions

- Parent school inquiry tracking and franchise lead tracking are different business funnels.
- Parent, franchise Canada, and franchise USA should keep separate GA4 properties.
- Parent, franchise Canada, and franchise USA should ultimately keep separate Meta datasets or pixels.
- Google Ads and Meta optimization events should not mix parent enrollment leads with franchise development leads.
- Shared code patterns are acceptable, but event contracts and destination mappings must stay property-specific.

## Franchise Canada Subdomain Caution

`franchise.cefa.ca` is a subdomain under `cefa.ca`, so production GTM changes need stricter containment than a fully separate domain.

Required GTM safeguards:

- Use hostname filters so parent tags fire only on parent hostnames and franchise tags fire only on franchise hostnames.
- Audit cross-domain and linker settings before publishing.
- Avoid broad all-pages triggers that can unintentionally fire parent tags on the franchise subdomain.
- Check first-party cookie domain behavior before porting parent attribution logic to franchise Canada.
- Keep parent and franchise dataLayer event names distinct unless the event is intentionally shared and separated by `site_context` or equivalent metadata.

Recommended franchise event direction:

- Parent submit: `school_inquiry_submit` mapped to GA4 `generate_lead`.
- Franchise Canada submit: use a franchise-specific website event such as `franchise_inquiry_submit`.
- Franchise USA submit: use a franchise-specific website event such as `franchise_inquiry_submit`, but keep USA destination mappings separate from Canada.

## Meta Dataset Recommendation

Current known risk:

- Agency has reportedly placed parent, franchise Canada, and franchise USA events under the same Meta dataset/pixel.
- The Ads Manager accounts may be separate, but a shared dataset still mixes event history, audiences, diagnostics, and CAPI/dedup scope.

Recommendation:

- Separate USA definitely before serious production optimization.
- Prefer separating franchise Canada from parent as well, because the business funnel is different: parent enrollment vs franchise development.
- If there is concern about losing Meta learning, do not switch optimization abruptly. Run a transition period where the current dataset remains stable while the separate franchise dataset is prepared, tested, and validated.
- Do not optimize franchise campaigns against the parent enrollment lead event unless that is an intentional short-term compromise.

Practical transition model:

- Phase A: keep current shared dataset only for continuity while auditing live events and campaign dependencies.
- Phase B: create/prepare separate franchise Canada and USA datasets, with clean event names and test events.
- Phase C: move new franchise optimization to the separated dataset once event quality is proven.
- Phase D: keep historical shared-dataset reporting available, but stop treating it as the clean future architecture.

Why not keep everything shared forever:

- Parent and franchise leads train different signals.
- Shared datasets make audience quality and funnel diagnostics harder to interpret.
- CAPI/server-side dedup becomes riskier when unrelated funnels share event names and IDs.
- USA has different domain, market, sales motion, and likely compliance/reporting needs.

## What Needs GPT Pro Review

The current CEFA plan already says separate Meta datasets or pixels are required for parent, franchise Canada, and franchise USA. A GPT Pro review is optional, not required, if the question is only whether separation belongs in the plan.

Ask GPT Pro only if we want a deeper transition strategy for:

- preserving Meta learning while separating datasets,
- mapping old campaign optimization events to new separated events,
- phased CAPI rollout across parent, franchise Canada, and franchise USA,
- naming conventions for franchise-specific event contracts.

## Next Franchise Work

- [ ] Audit live `franchise.cefa.ca` GTM container and destination IDs.
- [ ] Audit live `www.franchisecefa.com` GTM container and destination IDs.
- [ ] Identify all franchise Canada forms, CTAs, thank-you flows, and CRM handoffs.
- [ ] Identify all franchise USA forms, CTAs, thank-you flows, and CRM handoffs.
- [ ] Confirm GA4 property IDs for franchise Canada and franchise USA.
- [ ] Confirm Meta datasets/pixels currently used by parent, franchise Canada, and franchise USA.
- [ ] Decide whether Canada franchise gets a new dataset immediately or after a short transition period.
- [ ] Separate USA dataset/pixel before serious USA production optimization.
