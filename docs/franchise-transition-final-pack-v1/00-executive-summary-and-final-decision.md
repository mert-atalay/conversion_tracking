# CEFA Franchise Transition Tracking — Final Strategic Recommendation

## Final decision

Use a **sequenced transition**, not an abrupt rebuild.

```text
Parent Canada = keep helper-plugin/GTM model and cut to production first
Franchise Canada = stabilize inside current shared Meta dataset first, then migrate gradually
Franchise USA = create separate measurement boundaries before serious optimization
sGTM = Phase 2, not a blocker for franchise Phase 1 tracking
```

## Why

The parent implementation has moved past the earlier proof-of-concept concern. The current parent staging result is now a CEFA-owned helper-plugin event where one confirmed Form 4 submission produces one `school_inquiry_submit`, the browser `event_id` matches Gravity Forms field `32.4`, and school/program/day values are clean separate fields.

The open risk is no longer whether the parent event can work. The open risk is **cross-surface contamination**, especially because:

- `franchise.cefa.ca` is a subdomain under `cefa.ca`.
- Parent, franchise Canada, and franchise USA have reportedly been routed through the same Meta dataset/pixel.
- Canada franchise campaigns may already rely on that shared Meta dataset.
- USA franchise is a different domain, market, and business surface.

## Core recommendation by surface

### Parent Canada — `cefa.ca`
Keep the helper plugin + GTM model.

Do not delete legacy GTM/GA4 assets until production cutover is completed and verified. Keep micro-conversions out of bidding unless explicitly approved.

### Franchise Canada — `franchise.cefa.ca`
Do **not** abruptly move active campaigns away from the current shared Meta dataset if live optimization depends on it.

Instead:

1. Add strict GTM hostname containment.
2. Fire clean franchise-specific website events and parameters.
3. Create franchise Canada custom conversions inside the existing shared dataset.
4. Build/test a separate franchise Canada Meta dataset in parallel.
5. Migrate campaigns gradually only after signal quality is proven.

### Franchise USA — `www.franchisecefa.com`
Default to a separate Meta dataset/pixel before serious production optimization.

If any USA campaigns are already live on the shared dataset, audit them before changing, but the clean future state should be separated from day one for new serious optimization.

## What not to do

- Do not let parent tags fire on franchise hosts.
- Do not let franchise tags fire on parent pages.
- Do not use the same raw website event name for parent inquiry and franchise lead.
- Do not abruptly change the optimization event or dataset for active Canada franchise campaigns.
- Do not make sGTM a Phase 1 blocker.
- Do not keep the shared Meta dataset forever as the clean architecture.
