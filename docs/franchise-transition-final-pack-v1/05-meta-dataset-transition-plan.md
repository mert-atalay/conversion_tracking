# Meta Dataset Transition Plan

## Final answer

### Parent Canada and Franchise Canada

Do not split immediately if Canada franchise live campaigns rely on the shared dataset.

Use a phased transition:

```text
Shared dataset temporarily -> separated events/custom conversions -> parallel new dataset -> gradual campaign migration -> final separation
```

### Franchise USA

Separate by default before serious production optimization.

## Why not split Canada immediately?

The current handoff says Canada franchise campaigns rely on the shared dataset. Changing the dataset/pixel or optimization event can weaken or reset Meta optimization because campaigns need stable conversion signals to learn.

Therefore, immediate separation may create unnecessary performance risk.

## Why not keep shared forever?

Parent enrollment leads and franchise development leads are different outcomes.

Long-term shared datasets create problems:

- mixed audiences
- mixed diagnostics
- unclear lead quality
- harder CAPI dedup
- difficult reporting by business unit
- parent `Lead` and franchise `Lead` become hard to interpret

## Phase A — stabilize shared dataset

Keep current shared dataset for active Canada franchise campaigns.

Add parameters:

```js
{
  site_context: "franchise_ca",
  business_unit: "franchise",
  market: "canada",
  country: "CA",
  lead_type: "franchise_lead",
  form_family: "franchise_inquiry",
  event_id: "<unique id>",
  event_source_url: "<full URL>",
  tracking_source: "gtm_or_helper_plugin"
}
```

Create custom conversions inside the shared dataset:

```text
Parent Inquiry Lead
Franchise Canada Lead
Franchise Canada Site Submission
Franchise Canada CTA Click (optional/reporting only)
```

Rules should use:

```text
event = Lead or franchise event
AND site_context = franchise_ca
AND host contains franchise.cefa.ca
```

## Phase B — prepare separate datasets

Create or identify:

```text
Parent dataset
Franchise Canada dataset
Franchise USA dataset
```

Install/test events without changing live optimization.

Use Meta Events Manager test events and diagnostics.

## Phase C — gradual Canada migration

Do not edit all active ad sets at once.

Recommended migration options:

1. Launch new campaigns/ad sets on the new franchise Canada dataset.
2. Duplicate a controlled test campaign/ad set.
3. Compare event volume, match quality, CPL, lead quality, and conversion lag.
4. Move active campaigns only once the new dataset has enough reliable signal.

## Phase D — final separation

Final target:

```text
Parent Canada -> parent dataset
Franchise Canada -> franchise Canada dataset
Franchise USA -> franchise USA dataset
```

Historical shared dataset remains for old reporting, not clean future optimization.

## CAPI timing

For Canada franchise:

- If active campaigns still optimize against the shared dataset, first CAPI implementation should target the **currently optimized dataset** to preserve continuity.
- Test the separate dataset in parallel.
- Switch CAPI destination as campaigns migrate.

For USA:

- Send CAPI to the USA dataset when implemented.
