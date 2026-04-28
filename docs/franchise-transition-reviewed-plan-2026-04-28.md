# CEFA Franchise Transition Reviewed Plan

Last updated: 2026-04-28

This document records the reviewed position after comparing the CEFA parent tracking implementation, the franchise-transition handoff, and GPT Pro's final strategy pack.

## Final Position

The GPT Pro pack is directionally correct and should be adopted with one operational clarification: Canada franchise should only remain on the shared Meta dataset as a transition step, not as the target architecture.

Recommended order:

1. Finish parent production cutover first.
2. Audit Canada franchise before changing live campaign optimization.
3. Stabilize Canada franchise inside the currently optimized shared Meta dataset if active campaigns depend on it.
4. Build and test a separate Canada franchise dataset in parallel.
5. Separate USA franchise by default before serious production optimization.
6. Add CAPI after browser parity and event identity are stable.
7. Add custom-domain sGTM later as Phase 2 durability, not as a Phase 1 blocker.

## Accepted Adjustments To Our Plan

### Parent Canada

No strategy change.

The parent implementation remains:

- `CEFA Conversion Tracking` helper plugin.
- Confirmed-success `school_inquiry_submit`.
- Matching `event_id` between browser dataLayer and Gravity Forms field `32.4`.
- Clean Form 4 `32.*` school/program/day values.
- Attribution fields `35` through `46`.
- GTM as the destination mapping layer.
- No Gravity Forms Google Analytics Add-On as a final conversion source.

Parent production cutover should happen before major franchise rebuild work so the parent event contract does not drift while franchise decisions are being made.

### Franchise Canada

Adopt a phased transition.

Do not abruptly move active Canada franchise campaigns off the shared Meta dataset if those campaigns currently optimize against it. Instead, add clean franchise parameters and custom conversions inside the current dataset first:

```js
{
  site_context: "franchise_ca",
  business_unit: "franchise",
  market: "canada",
  country: "CA",
  lead_type: "franchise_lead",
  form_family: "franchise_inquiry",
  event_id: "<unique per submission>",
  event_source_url: window.location.href,
  tracking_source: "<gtm|helper_plugin>"
}
```

Then create and test a separate Canada franchise dataset in parallel before moving campaign optimization.

### Franchise USA

Default to a separate boundary:

- Separate Meta dataset/pixel.
- Separate GA4 property or confirmed isolated stream/reporting boundary.
- Dedicated GTM container where practical.
- Dedicated Google Ads conversion action family.

If there are already active USA campaigns using the shared dataset, audit before switching. Otherwise, do not inherit the parent/Canada shared dataset for new serious optimization.

### GTM

Separate containers per site family are preferred:

- Parent Canada.
- Franchise Canada.
- Franchise USA.

If a shared container is temporarily used, every base tag, conversion tag, trigger, lookup table, and destination mapping must be hostname-contained. This is especially important because `franchise.cefa.ca` is a subdomain under `cefa.ca`.

### Event Taxonomy

Keep website events neutral and map them in GTM:

| Surface | Website event | Destination example |
| --- | --- | --- |
| Parent inquiry | `school_inquiry_submit` | GA4 `generate_lead`, Meta `Lead`, Google Ads parent inquiry |
| Franchise inquiry | `franchise_inquiry_submit` | GA4 `generate_lead`, Meta `Lead`, Google Ads franchise inquiry |
| Real estate site submission | `real_estate_site_submit` | GA4 `generate_lead` or `site_submission_submit`, Meta `Lead` or custom conversion |

For franchise Canada and USA, use the same website event names where practical and separate with metadata:

```js
site_context: "franchise_ca" // or "franchise_us"
market: "canada" // or "usa"
country: "CA" // or "US"
business_unit: "franchise"
```

## Helper Plugin Direction

The shared codebase can be extended later, but not blindly.

Accepted direction:

- Keep the parent module stable.
- Add a configurable franchise module only after the franchise form stack and success flows are audited.
- Keep the plugin focused on identity, attribution, dataLayer payloads, and duplicate guards.
- Do not let the plugin replace franchise form handling, CRM delivery, Synuma/SiteZeus delivery, or agency-owned business logic.
- Do not send GA4, Google Ads, Meta, CAPI, or collector requests directly from the Phase 1 browser plugin.

The franchise module should be configuration-driven by site context, form family, success behavior, and environment.

## Open Questions For GPT Pro Or Internal Review

These are clarification questions, not blockers:

1. For franchise Canada GA4, is a separate property mandatory, or is a separate web stream plus strict reporting/BigQuery boundaries acceptable during transition?
2. For Meta Canada transition, should the shared dataset use the standard `Lead` event plus custom conversion rules, or a custom event name, before the separate dataset migration?
3. During the overlap period, should browser events be sent to both shared and new franchise Canada datasets for testing, or should the new dataset receive test-only traffic until campaign migration starts?
4. Should the configurable franchise plugin support non-Gravity Forms success detection first, or should we wait until the franchise form stack audit confirms the exact implementation?
5. What minimum event volume or test window should be required before moving active Canada franchise optimization from the shared dataset to the new dataset?

## Working Rule

The target architecture is separated by business funnel. The transition can temporarily preserve the shared Canada Meta dataset to avoid damaging active campaign learning, but the shared dataset should not become the permanent clean architecture.
