# Live Domain Controlled Submit Review

Last updated: 2026-04-30

## Scope

The new CEFA websites are now live on their original domains. This second review allowed controlled public form submissions, but no backend changes were made.

No website files, WordPress settings, GTM containers, GA4 properties, Google Ads conversion actions, Meta datasets, or Gravity Forms settings were changed.

Checked properties:

- Parent Canada: `https://cefa.ca`
- Franchise Canada: `https://franchise.cefa.ca`
- Franchise USA: `https://franchisecefa.com`

Evidence used:

- Live browser form submissions.
- Browser `window.dataLayer` inspection.
- Browser network request inspection for GA4, Google Ads, Meta, LinkedIn, GAConnector, and helper-plugin requests.
- GA4 MCP realtime/admin reads.
- Public DOM/form field inspection.
- Follow-up live WordPress saved-entry verification, documented in `docs/live-form-crm-integrity-review-2026-04-30.md`.

Follow-up saved-entry verification was completed after direct live WordPress MCP endpoint checks. Use `docs/live-form-crm-integrity-review-2026-04-30.md` as the current source for form/CRM integrity findings.

## Executive Status

| Property | Submit result | Current status | Main decision |
| --- | --- | --- | --- |
| `cefa.ca` | Form 4 submit passed | Parent browser-side contract and saved GF fields are working on live domain | Keep parent helper plugin active; verify KinderTales/business delivery before final signoff. |
| `franchise.cefa.ca` | Forms 1 and 2 submit, but final bridge missing | Not ready for final conversion mapping | Activate/deploy the franchise helper bridge or equivalent confirmed-success dataLayer event before GTM/Ads/Meta final mapping. |
| `franchisecefa.com` | Forms 1 and 2 submit, but final bridge missing | Measurement boundary improved, but event contract missing | Extend helper bridge to USA and configure USA GA4/GTM/custom dimensions before optimization. |

## Parent Canada: `cefa.ca`

### Controlled Submit Evidence

Test path:

```text
https://cefa.ca/submit-an-inquiry-today/?location=abbotsford-highstreet&utm_source=qa_tracking&utm_medium=live_audit&utm_campaign=conversion_migration_review&gclid=QA-GCLID-20260430
```

Submission result:

- Form `4` submitted successfully.
- Redirected to:
  - `https://cefa.ca/thank-you/?location=abbotsford-highstreet&inquiry=true`
- The helper plugin script was active:
  - `/wp-content/plugins/cefa-conversion-tracking/assets/js/cefa-conversion-tracking.js?ver=0.3.0`
- `window.dataLayer` contained exactly one `school_inquiry_submit`.
- `event_id` in dataLayer matched the pre-submit field `32.4`:
  - `76b3e864-d38a-4873-9f89-1d7fc7513ef3`

Confirmed dataLayer values included:

```js
{
  event: "school_inquiry_submit",
  event_id: "76b3e864-d38a-4873-9f89-1d7fc7513ef3",
  form_id: "4",
  form_family: "parent_inquiry",
  lead_type: "cefa_lead",
  lead_intent: "inquire_now",
  school_selected_id: "81236954-bcad-11ef-8bcb-028d36469a89",
  school_selected_slug: "abbotsford-highstreet",
  school_selected_name: "Abbotsford - Highstreet",
  program_id: "475",
  program_name: "Junior Kindergarten 1",
  days_per_week: "5 days",
  utm_source: "qa_tracking",
  gclid: "QA-GCLID-20260430",
  inquiry_success: true,
  tracking_source: "helper_plugin"
}
```

Destination evidence:

- GA4 `generate_lead` request fired to `G-T65G018LYB`.
- GA4 payload included helper-plugin metadata such as `event_id`, `form_id`, `form_family`, `lead_type`, `school_selected_id`, `school_selected_slug`, `program_id`, `program_name`, `days_per_week`, `tracking_source`, and `value=150`.
- Google Ads conversion request fired for conversion ID `802334988`, label `5_KbCJO3j_gCEIzSyv4C`, value `150`, currency `CAD`.
- Meta Pixel request fired to pixel `918227085392601` as custom event `Inquiry Submit`; `eid` matched the same `event_id`.
- GA4 realtime for property `267558140` included `generate_lead`.

### Parent Verdict

Parent Canada passes the Phase 1A browser-side contract.

Remaining parent items before production signoff:

- Saved Gravity Forms entry fields `32.*` and `35-46` were verified in the follow-up form/CRM review.
- Verify KinderTales/business delivery path, not only browser/destination tags or saved GF fields.
- Keep the helper plugin active and prevent any Gravity Forms GA Add-On or old thank-you trigger from becoming a second final conversion source.
- Clean up legacy-style reporting parameters later; current GTM still sends some `event_title` and `event_label` parameters on non-primary events, but the core submit event is already metadata-based.

## Franchise Canada: `franchise.cefa.ca`

### Form 1: Franchise Inquiry

Test path:

```text
https://franchise.cefa.ca/available-opportunities/franchising-inquiry/?utm_source=qa_tracking&utm_medium=live_audit&utm_campaign=franchise_ca_review&gclid=QA-FRCA-GCLID-20260430
```

Submission result:

- Form `1` submitted successfully.
- Redirected to:
  - `https://franchise.cefa.ca/inquiry-thank-you/?location=edmonton-ab&inquiry=true`
- Runtime IDs:
  - GTM: `GTM-TPJGHFS`
  - GA4: `G-6EMKPZD7RD`
- GAConnector cookies populated from the UTM/GCLID URL.
- Hidden GAConnector fields `14` through `30` were present, but blank in the rendered DOM before submit.
- No helper plugin was visible:
  - no helper script,
  - no `window.CEFAConversionTracking`,
  - no `franchise_inquiry_submit`,
  - no event ID in dataLayer.

Observed after submit:

- `window.dataLayer` had only standard GTM lifecycle objects such as `gtm.js`, `gtm.dom`, and `gtm.load`.
- No `franchise_inquiry_submit`.
- No `generate_lead` in dataLayer.
- No event_id.
- Browser network showed pageview/remarketing style hits, LinkedIn, and Meta `PageView`; no clean final franchise lead event.
- GA4 realtime for property `259747921` did not show `generate_lead` or a clean final submit event during the review window.

### Form 2: Real Estate Site Inquiry

Test path:

```text
https://franchise.cefa.ca/partner-with-cefa/real-estate-partners/submit-a-site/?utm_source=qa_tracking&utm_medium=live_audit&utm_campaign=franchise_ca_site_review&gclid=QA-FRCA-SITE-GCLID-20260430
```

Submission result:

- Form `2` submitted successfully.
- Redirected to:
  - `https://franchise.cefa.ca/site-thank-you/`
- Runtime IDs:
  - GTM: `GTM-TPJGHFS`
  - GA4: `G-6EMKPZD7RD`
- GAConnector cookies populated from the UTM/GCLID URL.
- Hidden GAConnector fields `14` through `30` were present, but blank in the rendered DOM before submit.
- No helper plugin was visible.

Observed after submit:

- `window.dataLayer` had only standard GTM lifecycle objects and `gtag get` callbacks.
- No `real_estate_site_submit`.
- No event_id.
- GA4 received pageview-style hits; the browser evidence did not show a GA4 `generate_lead` for this final site submission.
- Google Ads form_start/form_submit and remarketing-style requests were visible, but those are not the CEFA final conversion contract.
- Meta fired `PageView`, not a clean lead/site-submit event with dedup event ID.

### Franchise Canada Verdict

Franchise Canada is not ready for final conversion mapping.

The forms work, but the tracking source is still legacy/thank-you/pageview/form-auto-event based. It does not meet the agreed target:

```text
one confirmed successful submission
-> one neutral website-side event
-> one event_id
-> clean metadata
-> GTM maps that event to destinations
```

Required changes once backend changes are allowed:

- Deploy and activate the existing `CEFA Conversion Tracking` helper plugin `0.4.0`, or an equivalent website-side bridge.
- Emit `franchise_inquiry_submit` after confirmed Form `1` success only.
- Emit `real_estate_site_submit` after confirmed Form `2` success only.
- Generate/store a submission-scoped `event_id` in Gravity Forms entry meta or a dedicated hidden field.
- Include `site_context="franchise_ca"`, `business_unit="franchise"`, `market="canada"`, and `country="CA"`.
- Read GAConnector fields `14` through `30`; do not overwrite them unless saved-entry tests prove they are empty and we explicitly add a missing-value backfill.
- Add GA4 custom dimensions for the new helper-plugin parameters; current Canada Franchise custom dimensions are mostly legacy form/reporting fields such as `event_title`, `event_label`, `preferred_location`, `applicant_capital`, and click/page fields.
- Build hostname-contained GTM triggers from the helper events, not URL-only thank-you triggers.
- Keep Ads/Meta final conversion mapping gated until conversion labels and Meta dataset/custom-conversion decisions are confirmed.

## Franchise USA: `franchisecefa.com`

### Boundary Correction Since Earlier Read-Only Audit

The earlier read-only audit saw USA using the Canada franchise public IDs. The controlled submit review found the live USA site now uses separate visible IDs:

- GTM: `GTM-5LZMHBZL`
- GA4: `G-YL1KQPWV0M`

This is a positive change and should replace the earlier boundary-mismatch finding. USA still does not have the required confirmed-success event bridge.

GA4 admin evidence:

- USA property: `properties/519783092` / `CEFA Franchise - USA.`
- Time zone: `America/Los_Angeles`
- Currency currently `CAD`
- Google Ads links:
  - `3820636025`
  - `4159217891`
- Custom dimensions/metrics: none currently registered.

### Form 1: Franchise Inquiry

Test path:

```text
https://franchisecefa.com/available-opportunities/franchising-inquiry/?utm_source=qa_tracking&utm_medium=live_audit&utm_campaign=franchise_us_review&gclid=QA-FRUS-GCLID-20260430
```

Submission result:

- Form `1` submitted successfully.
- Redirected to:
  - `https://franchisecefa.com/inquiry-thank-you/?location=atlanta&inquiry=true`
- GAConnector cookies populated.
- Hidden GAConnector fields `14` through `30` were present, but blank in the rendered DOM before submit.
- No helper plugin was visible.

Observed after submit:

- `window.dataLayer` had only `gtm.js`, `gtm.dom`, `gtm.load`, and `gtag get` callbacks.
- No `franchise_inquiry_submit`.
- No event_id.
- GA4 realtime for property `519783092` showed `form_start` and `form_submit`, but not `generate_lead`.
- Browser network showed pageview/remarketing style requests and Meta `PageView`; no clean lead event with event ID.

### Form 2: Real Estate Site Inquiry

Test path:

```text
https://franchisecefa.com/partner-with-cefa/real-estate-partners/submit-a-site/?utm_source=qa_tracking&utm_medium=live_audit&utm_campaign=franchise_us_site_review&gclid=QA-FRUS-SITE-GCLID-20260430
```

Submission result:

- Form `2` submitted successfully.
- Redirected to:
  - `https://franchisecefa.com/site-thank-you/`
- GAConnector cookies populated.
- Hidden GAConnector fields `14` through `30` were present, but blank in the rendered DOM before submit.
- No helper plugin was visible.

Observed after submit:

- `window.dataLayer` had only standard GTM lifecycle objects and `gtag get` callbacks.
- No `real_estate_site_submit`.
- No event_id.
- Browser network showed GA4 pageview, Google Ads remarketing/config requests, and Meta `PageView`, not a final clean site-submit conversion event.

### Franchise USA Verdict

Franchise USA has made progress on measurement separation, but it is not ready for final conversion mapping.

Required changes once backend changes are allowed:

- Extend the helper plugin to support `franchisecefa.com`.
- Emit the same neutral event names as Canada:
  - `franchise_inquiry_submit`
  - `real_estate_site_submit`
- Differentiate USA with metadata:
  - `site_context="franchise_us"`
  - `business_unit="franchise"`
  - `market="usa"`
  - `country="US"`
- Generate/store a submission-scoped `event_id`.
- Read GAConnector fields `14` through `30`; keep GAConnector as the attribution source for now.
- Register USA GA4 custom dimensions before relying on reporting for helper-plugin metadata.
- Keep USA GTM/GA4 separated from Canada; do not regress to the shared Canada IDs.
- Confirm the USA Meta dataset/pixel and Google Ads conversion action strategy before final platform mapping.

## Cross-Property Findings

### What Changed Since The First Read-Only Audit

- Parent `cefa.ca` is now proven with a controlled successful Form `4` submit.
- Franchise Canada Forms `1` and `2` are proven to submit, but not to emit the target CEFA events.
- Franchise USA Forms `1` and `2` are proven to submit.
- USA public runtime now shows a separate GTM/GA4 stack, not the Canada IDs seen earlier.
- GA4 MCP access works and confirms property/admin state.

### What Is Still Missing

- Franchise Canada and USA do not have the confirmed-success dataLayer bridge live.
- Franchise Canada and USA do not expose submission-scoped `event_id` values to browser dataLayer.
- Franchise Canada and USA do not currently provide clean metadata-rich final events for GTM.
- Franchise Canada and USA still rely on pageview/form-auto-event behavior that can be useful diagnostically but is not enough for final Ads/Meta conversion truth.
- Follow-up saved-entry verification found franchise GAConnector fields `14-30` blank in live browser submissions and two Synuma lead-ID gaps; see `docs/live-form-crm-integrity-review-2026-04-30.md`.

### Do Not Do

- Do not map final Ads/Meta conversions from URL-only thank-you triggers.
- Do not treat GA4 automatic `form_submit` as the final conversion source.
- Do not rely on Meta `PageView` or Google Ads remarketing/config hits as final lead proof.
- Do not move franchise Canada active campaigns to a new Meta dataset abruptly until the dataset transition plan is approved.
- Do not use micro-conversions as Google Ads primary bidding conversions at launch.

## Prepared Change List

### Parent Canada

- Keep `CEFA Conversion Tracking` active.
- Keep GTM mapping from `school_inquiry_submit` to GA4 `generate_lead`, Ads, and Meta.
- Gravity Forms saved entry values are verified; still verify KinderTales/business delivery if separate from GF.
- Confirm old Gravity Forms GA Add-On/temporary triggers are not mapped as duplicate final conversions.
- Update docs that the live parent route is `/submit-an-inquiry-today/`, not `/inquire-form/`.

### Franchise Canada

- Activate/deploy helper plugin `0.4.0` or equivalent on `franchise.cefa.ca`.
- Test Form `1` and Form `2` again after activation.
- Verify `franchise_inquiry_submit` and `real_estate_site_submit` in dataLayer.
- Verify event IDs are saved in entries.
- Verify GAConnector fields `14-30` are saved in entries.
- Register target GA4 custom dimensions.
- Build hostname-contained GTM tags from helper events.
- Configure GA4 first; gate Ads/Meta final mappings until labels/dataset/custom conversions are confirmed.

### Franchise USA

- Extend the helper plugin to `franchisecefa.com`.
- Add `franchise_us` metadata and USA-specific event payload values.
- Register USA GA4 custom dimensions; the USA property currently has no custom definitions.
- Keep `GTM-5LZMHBZL` / `G-YL1KQPWV0M` or the approved USA equivalents separate from Canada.
- Confirm USA Meta pixel/dataset and Google Ads conversions before optimization.

### Later Strengthening

- Phase 1B: add collector/CAPI after browser event identity is stable.
- Phase 2: add custom-domain sGTM after browser parity and dataset transition are stable.
- Keep BigQuery/warehouse as the durable truth target, but do not block browser parity on sGTM.

## Final Signoff Position

Parent Canada is browser-side ready, pending backend/saved-entry confirmation.

Franchise Canada and Franchise USA are not ready for final paid-media conversion mapping yet. They need the helper-plugin bridge or equivalent confirmed-success dataLayer implementation before we should map final GA4, Google Ads, Meta, or LinkedIn conversion events.
