# Cross-Property Measurement Boundaries

Last updated: 2026-04-30

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
- Website events should stay neutral and GTM should map them to GA4, Google Ads, Meta, and later CAPI/sGTM destinations.

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

- Separate USA by default before serious production optimization.
- Prefer separating franchise Canada from parent as the target architecture, because the business funnel is different: parent enrollment vs franchise development.
- If Canada franchise live campaigns currently rely on the shared dataset, do not switch optimization abruptly. Use a transition period where the current dataset remains stable while the separate franchise dataset is prepared, tested, and validated.
- Do not optimize franchise campaigns against the parent enrollment lead event unless that is an intentional short-term compromise.

Practical transition model:

- Phase A: keep current shared Canada dataset only for continuity while auditing live events and campaign dependencies.
- Phase B: add clean franchise parameters such as `site_context`, `business_unit`, `market`, `country`, `lead_type`, `form_family`, `event_id`, and `event_source_url`.
- Phase C: create shared-dataset custom conversions for `Franchise Canada Lead` and `Franchise Canada Site Submission`.
- Phase D: create/prepare separate franchise Canada and USA datasets with clean test events.
- Phase E: move new or duplicated franchise optimization to the separated dataset once event quality is proven.
- Phase F: keep historical shared-dataset reporting available, but stop treating it as the clean future architecture.

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

- [x] Run first read-only public audit after the new sites moved to live domains.
- [ ] Confirm whether USA should be documented and configured against apex `franchisecefa.com`, `www.franchisecefa.com`, or both.
- [ ] Audit live `franchise.cefa.ca` GTM container and destination IDs with authenticated GTM access before making changes.
- [ ] Audit live `franchisecefa.com` GTM container and destination IDs with authenticated GTM access before making changes.
- [ ] Identify all franchise Canada forms, CTAs, thank-you flows, and CRM handoffs.
- [ ] Identify all franchise USA forms, CTAs, thank-you flows, and CRM handoffs.
- [ ] Confirm GA4 property IDs for franchise Canada and franchise USA.
- [ ] Confirm Meta datasets/pixels currently used by parent, franchise Canada, and franchise USA.
- [ ] Confirm whether active Canada franchise campaigns are optimizing against the shared parent/franchise dataset.
- [ ] Keep Canada franchise on the shared dataset only as a controlled transition if active campaigns depend on it.
- [ ] Create franchise Canada custom conversions inside the shared dataset using franchise-specific parameters before campaign migration.
- [ ] Separate USA dataset/pixel before serious USA production optimization.

## 2026-04-30 Live Migration Read-Only Status

See [Live migration read-only audit, 2026-04-30](./live-migration-readonly-audit-2026-04-30.md).

Key updates from the first live-domain check:

- Parent `cefa.ca` still exposes the helper plugin and Form 4 on `/submit-an-inquiry-today/`.
- Parent old `/inquire-form/` route now returns `404`; action plans should use the new live inquiry path.
- Franchise Canada exposes Forms `1` and `2`, `GTM-TPJGHFS`, GAConnector scripts, and hidden fields `14` through `30`, but the helper-plugin success events are not publicly visible.
- Franchise USA currently appears to use `GTM-TPJGHFS` and `G-6EMKPZD7RD`, matching the Canada franchise stack rather than a clearly separated USA boundary.
- Local ADC was refreshed after the read-only audit, and GA4 MCP read access now confirms a separate USA property exists: `properties/519783092` / `CEFA Franchise - USA.` The public USA site still needs verification/correction because it visibly loads the Canada franchise measurement ID.
- No final Ads or Meta mapping should be treated as ready until controlled submissions and destination checks are completed.
