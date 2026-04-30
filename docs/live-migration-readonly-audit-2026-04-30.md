# Live Migration Read-Only Audit

Last updated: 2026-04-30

## Scope

The new CEFA websites are now live on their original domains while migration work is still in progress.

This audit is read-only. No website files, WordPress settings, GTM containers, GA4 properties, Ads accounts, Meta datasets, or forms were changed. No form submissions were completed.

Checked surfaces:

- Parent Canada: `https://cefa.ca`
- Franchise Canada: `https://franchise.cefa.ca`
- Franchise USA: `https://www.franchisecefa.com` / `https://franchisecefa.com`

Evidence methods:

- Public HTTP checks.
- Browser/runtime checks with Chrome DevTools.
- Public page source and rendered DOM inspection.
- Public GTM snippet/container-string inspection where available.

Authenticated GA4 reads were attempted but were not available in this session because local Google Application Default Credentials require reauthentication. Authenticated GTM, GA4, Ads, and Meta admin checks therefore remain pending.

Because no forms were submitted, confirmed-success dataLayer events, Gravity Forms entries, GA4 receipt, Google Ads receipt, Meta receipt, and CRM delivery remain pending validation.

## Executive Status

| Property | Current read-only status | Main conclusion |
| --- | --- | --- |
| `cefa.ca` | Mostly intact, pending controlled submit test | Parent helper-plugin surface is live on the final domain and Form 4 is present on the new inquiry path. |
| `franchise.cefa.ca` | Partially intact, not ready for final conversion mapping | Forms, GTM, and GAConnector are present, but the planned helper-plugin confirmed-success events are not publicly visible. |
| `franchisecefa.com` | Not aligned with the target boundary plan | USA appears to be using the Canada franchise GTM/GA4 stack and does not yet show USA-separated tracking. |

## Parent Canada: `cefa.ca`

### Verified Read-Only Findings

- `https://cefa.ca/` returns `200`.
- `https://www.cefa.ca/` redirects to `https://cefa.ca/`.
- GTM visible on sampled pages: `GTM-NZ6N7WNC`.
- CEFA Conversion Tracking helper plugin script is visible:
  - `/wp-content/plugins/cefa-conversion-tracking/assets/js/cefa-conversion-tracking.js?ver=0.3.0`
- New live inquiry route works:
  - `https://cefa.ca/submit-an-inquiry-today/`
- Old route currently returns `404`:
  - `https://cefa.ca/inquire-form/`
- Form 4 is present on the new inquiry route:
  - `gform_4`
- The rendered form exposes the expected parent tracking fields:
  - Field `32.1`: selected school ID value
  - Field `32.2`: program ID
  - Field `32.3`: days per week
  - Field `32.4`: generated event ID
  - Field `32.5`: selected school slug
  - Field `32.6`: selected school name
  - Field `32.7`: program name
  - Fields `35` through `46`: attribution fields
- A URL with UTM parameters populated Form 4 attribution fields in the rendered DOM.
- Direct visit to the thank-you URL did not expose a `school_inquiry_submit` event in the browser dataLayer during the read-only check.

### Parent Risks And Open Items

- A controlled real Form 4 submission is still required to prove:
  - one confirmed `school_inquiry_submit`,
  - event ID match between browser payload and Gravity Forms field `32.4`,
  - saved entry values for fields `32.*` and `35-46`,
  - GA4 `generate_lead` receipt,
  - no duplicate Ads/Meta destination firing.
- One sampled school rendered a numeric selected-school value where the plan expects a CEFA-owned `school_uuid`. This may be valid migrated school data, but it needs confirmation before final reporting joins or CRM matching depend on it.
- Some public school-page CTA links may not include a `location=` query in raw HTML. This needs click-path testing to confirm whether JavaScript/session logic preserves school context before submit.

### Parent Current Classification

Parent Canada is the most intact property after migration. It is not fully signed off until a controlled Form 4 submission and destination checks are completed on the final domain.

## Franchise Canada: `franchise.cefa.ca`

### Verified Read-Only Findings

- `http://franchise.cefa.ca` redirects to `https://franchise.cefa.ca/`.
- `https://franchise.cefa.ca/` returns `200`.
- GTM visible on sampled pages:
  - `GTM-TPJGHFS`
- GA4 measurement ID visible from the runtime/container surface:
  - `G-6EMKPZD7RD`
- Gravity Forms are present:
  - Form `1` on `/available-opportunities/franchising-inquiry/`
  - Form `2` on `/partner-with-cefa/real-estate-partners/`
  - Form `2` on `/partner-with-cefa/real-estate-partners/submit-a-site/`
- GAConnector scripts are active:
  - `tracker.gaconnector.com/gaconnector-server.js`
  - `tc.gaconnector.com/gaconnector.js`
- GAConnector cookies were set from UTM test URLs.
- Hidden GAConnector-style fields `14` through `30` are present on Forms `1` and `2`.

### Franchise Canada Gaps

- The CEFA Conversion Tracking helper plugin was not publicly visible on Franchise Canada:
  - no visible helper script,
  - no visible `CEFAConversionTracking` browser config,
  - no public evidence of the REST namespace,
  - no visible `franchise_inquiry_submit`,
  - no visible `real_estate_site_submit`.
- GAConnector cookies were populated, but fields `14` through `30` were still blank in the rendered form DOM during the read-only check.
- Public checks cannot prove whether GAConnector writes values into saved Gravity Forms entries at submission time.
- The public GTM/container surface still appears legacy-heavy, including old-style form submit strings and thank-you/pageview logic.

### Franchise Canada Current Classification

Franchise Canada has the live form surfaces and legacy tracking stack in place, but the planned CEFA-owned confirmed-success event bridge is not active or not publicly verifiable. Do not map final GA4, Google Ads, or Meta conversions from this property until a controlled Form 1 and Form 2 test proves clean success events and saved-entry attribution.

## Franchise USA: `franchisecefa.com`

### Verified Read-Only Findings

- `https://www.franchisecefa.com/` redirects to `https://franchisecefa.com/`.
- The canonical host appears to be the apex domain:
  - `https://franchisecefa.com/`
- GTM visible on sampled pages:
  - `GTM-TPJGHFS`
- GA4 measurement ID visible from the runtime/container surface:
  - `G-6EMKPZD7RD`
- Gravity Forms are present:
  - Form `1` on `/available-opportunities/franchising-inquiry/`
  - Form `2` on `/partner-with-cefa/real-estate-partners/submit-a-site/`
- GAConnector scripts are active.
- Hidden GAConnector-style fields `14` through `30` are present.
- Public thank-you pages are directly visitable:
  - `/inquiry-thank-you/`
  - `/site-thank-you/`

### Franchise USA Gaps

- USA currently appears to be using the same visible GTM and GA4 stack as Franchise Canada.
- No separate USA helper-plugin surface was visible.
- No visible `franchise_inquiry_submit`, `real_estate_site_submit`, event ID, or helper-plugin dataLayer bridge was found.
- The shared container surface includes Canada/dev references and old-style selectors that may not match the live Gravity Forms markup.
- Public thank-you pages create false-positive risk if GTM uses URL-only thank-you triggers.

### Franchise USA Current Classification

Franchise USA is not aligned with the target cross-property measurement boundary yet. Before serious production optimization, USA needs separated or strictly hostname-contained GTM, GA4, Meta, and Ads mappings.

## Cross-Property Risks

### Critical

- Do not treat Franchise Canada or Franchise USA as ready for final paid-media conversion mapping just because GTM and Gravity Forms are present.
- USA currently appears to share the Canada franchise GTM/GA4 stack, which conflicts with the target plan for separated USA measurement.
- URL-only thank-you tracking is still a false-positive risk on franchise properties unless guarded by a confirmed submission signal.

### High

- Franchise Canada planned helper-plugin version `0.4.0` is not visibly active on the live domain.
- GAConnector cookies are active, but field writeback into the form DOM and saved entries is not yet proven.
- Parent is close, but still needs a controlled final-domain submission to prove backend/browser/destination parity.

### Medium

- Parent route changed from the older `/inquire-form/` assumption to `/submit-an-inquiry-today/`.
- Parent school identity values need a sample review for UUID consistency.
- Franchise USA canonical host resolves to apex `franchisecefa.com`, so docs and GTM host rules should include the apex host, not only `www.franchisecefa.com`.

## Updated Action Plan

### Step 1: Parent Final-Domain Validation

Do this first because parent is closest to the planned state.

- Run one controlled Form 4 submission on `cefa.ca`.
- Confirm one `school_inquiry_submit` event in dataLayer.
- Confirm `event_id` equals Gravity Forms field `32.4`.
- Confirm fields `32.1` through `32.7` save as clean separate values.
- Confirm fields `35` through `46` save attribution values.
- Confirm direct thank-you visits and reloads do not produce false conversions.
- Confirm GA4 receives `generate_lead` with the helper-plugin metadata.
- Confirm Ads/Meta are not receiving duplicate final conversions.

### Step 2: Franchise Canada Bridge Activation Or Decision

- Decide whether to activate the existing CEFA Conversion Tracking plugin `0.4.0` on the live Franchise Canada site or rebuild the same bridge in another approved deployment path.
- Run one controlled Form 1 submission.
- Run one controlled Form 2 submission.
- Confirm `franchise_inquiry_submit` and `real_estate_site_submit` exist only after confirmed success.
- Confirm event IDs are saved in Gravity Forms entry meta or a dedicated hidden field.
- Confirm GAConnector fields `14` through `30` are saved in entries.
- If GAConnector fields remain empty, decide whether the helper plugin should backfill missing attribution from cookies/URL parameters.

### Step 3: Franchise Canada GTM/GA4 Mapping

Only after Step 2 passes:

- Create hostname-contained triggers for `franchise.cefa.ca`.
- Map `franchise_inquiry_submit` and `real_estate_site_submit` to GA4 reporting.
- Keep micro-conversions out of bidding.
- Keep Google Ads and Meta final conversion mapping gated until labels, datasets, and campaign dependency decisions are confirmed.

### Step 4: Franchise USA Boundary Correction

- Confirm whether USA should use a separate GTM container immediately or a strictly hostname-contained temporary shared container.
- Confirm the intended USA GA4 property and Meta dataset/pixel.
- Confirm whether the current visible `GTM-TPJGHFS` / `G-6EMKPZD7RD` setup is temporary or accidental.
- Extend the helper-plugin contract to USA or create an equivalent USA bridge after form IDs and field IDs are verified.
- Do not optimize USA campaigns against the shared Canada franchise event stream unless explicitly approved as a temporary transition.

### Step 5: Platform Strengthening

After browser parity is proven:

- Add or verify GA4 custom dimensions for each property.
- Confirm Google Ads primary/secondary conversion actions.
- Confirm Meta custom conversions and dataset transition plan.
- Add CAPI/server-side delivery only after event IDs and browser events are stable.
- Keep sGTM as the attribution-strengthening phase, not a blocker for the immediate live-site integrity check.

## Current Signoff Position

The live migration did not erase the parent tracking bridge, and the parent property appears close to the planned Phase 1A model.

The franchise properties are not yet ready for final conversion mapping:

- Franchise Canada needs the planned confirmed-success bridge activated or otherwise proven.
- Franchise USA needs measurement-boundary correction before production optimization.

No cleanup of old GTM/GA4/Ads/Meta assets should happen until the controlled submission tests prove the new live-domain path end to end.
