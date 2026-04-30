# CEFA Conversion Tracking

Lightweight WordPress plugin for CEFA conversion tracking.

This plugin emits clean CEFA `dataLayer` events for confirmed inquiry conversions, Phase 1A browser micro-conversions, and attribution handoff.

It does not replace Gravity Forms, CEFA School Manager, CEFA Franchise API, Field 32 UI, location sync, KinderTales, GAConnector, GTM, or platform tags.

## What It Owns

- Ensures Form 4 field `32.4` has a unique submission-scoped `event_id`.
- Supports Franchise Canada Form 1 and Form 2 with event IDs stored as Gravity Forms entry meta.
- Uses the saved Gravity Forms entry as the source of truth.
- Creates a short-lived one-time thank-you-page token after successful submission.
- Pushes one clean `school_inquiry_submit` event into `window.dataLayer`.
- Pushes one clean `franchise_inquiry_submit` event for Franchise Canada Form 1.
- Pushes one clean `real_estate_site_submit` event for Franchise Canada Form 2.
- Prevents direct thank-you-page false positives and reload duplicates.
- Pushes plugin-owned micro-conversion events for inquiry CTA clicks, Find a School clicks, phone clicks, email clicks, Form 4 starts, submit attempts, and validation errors.
- Stores first-touch and last-touch attribution in the same first-party cookie pattern used by the old parent site.
- Backfills Form 4 attribution fields `35` through `46` before submission if they are empty.
- Reads Franchise Canada GAConnector hidden fields `14` through `30` when present; it does not overwrite them.
- Uses GA4-style structured metadata instead of legacy Universal Analytics event category/action/label fields.

## What It Does Not Own

- Form 4 UI.
- CEFA School Manager school/program/day behavior.
- Field 32 structure.
- School locking.
- Location sync.
- School Manager location cookies/session state.
- KinderTales/business submission delivery.
- CEFA Franchise API delivery.
- GAConnector attribution capture on franchise forms.
- GA4, Google Ads, Meta, CAPI, Measurement Protocol, collector, or sGTM outbound calls.

## Required Runtime

- WordPress `6.3+`.
- PHP `7.4+`.
- Gravity Forms with Form ID `4`.
- CEFA School Manager continuing to populate Form 4 field `32.*` values.
- Franchise Canada forms require Gravity Forms Form `1` / Franchise Inquiry and Form `2` / Site Inquiry.

## DataLayer Contract

### Parent Form 4

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: "school_inquiry_submit",
  event_id: "<same as 32.4>",
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

### Franchise Canada Form 1

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: "franchise_inquiry_submit",
  event_id: "<stored in Gravity Forms entry meta>",
  event_scope: "primary",
  site_context: "franchise_ca",
  business_unit: "franchise",
  market: "canada",
  country: "CA",
  form_id: "1",
  form_family: "franchise_inquiry",
  lead_type: "franchise_lead",
  lead_intent: "franchise_inquiry",
  location_interest: "<field 32>",
  investment_range: "<field 7>",
  opening_timeline: "<field 10>",
  school_count_goal: "<field 11>",
  ownership_structure: "<field 12>",
  lc_source: "<field 14>",
  lc_medium: "<field 15>",
  lc_campaign: "<field 16>",
  lc_content: "<field 17>",
  lc_term: "<field 18>",
  lc_channel: "<field 19>",
  lc_landing: "<field 20>",
  lc_referrer: "<field 21>",
  fc_source: "<field 22>",
  fc_medium: "<field 23>",
  fc_campaign: "<field 24>",
  fc_content: "<field 25>",
  fc_term: "<field 26>",
  fc_channel: "<field 27>",
  fc_referrer: "<field 28>",
  gclid: "<field 29>",
  ga_client_id: "<field 30>",
  inquiry_success: true,
  inquiry_success_url: window.location.href,
  tracking_source: "helper_plugin"
});
```

### Franchise Canada Form 2

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: "real_estate_site_submit",
  event_id: "<stored in Gravity Forms entry meta>",
  event_scope: "primary",
  site_context: "franchise_ca",
  business_unit: "franchise",
  market: "canada",
  country: "CA",
  form_id: "2",
  form_family: "site_inquiry",
  lead_type: "real_estate_lead",
  lead_intent: "submit_a_site",
  site_offered_by: "<field 39>",
  property_square_footage_range: "<field 34>",
  outdoor_space_range: "<field 35>",
  availability_timeline: "<field 36>",
  lc_source: "<field 14>",
  lc_medium: "<field 15>",
  lc_campaign: "<field 16>",
  lc_content: "<field 17>",
  lc_term: "<field 18>",
  lc_channel: "<field 19>",
  lc_landing: "<field 20>",
  lc_referrer: "<field 21>",
  fc_source: "<field 22>",
  fc_medium: "<field 23>",
  fc_campaign: "<field 24>",
  fc_content: "<field 25>",
  fc_term: "<field 26>",
  fc_channel: "<field 27>",
  fc_referrer: "<field 28>",
  gclid: "<field 29>",
  ga_client_id: "<field 30>",
  inquiry_success: true,
  inquiry_success_url: window.location.href,
  tracking_source: "helper_plugin"
});
```

## Micro-Conversion Events

The plugin also pushes these browser-side events into `window.dataLayer`:

- `parent_inquiry_cta_click`
- `find_a_school_click`
- `phone_click`
- `email_click`
- `form_start`
- `form_submit_click`
- `validation_error`

Example micro-conversion payload:

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: "parent_inquiry_cta_click",
  event_id: "<unique micro-event ID>",
  event_scope: "micro",
  page_context: "parent",
  page_type: "school",
  page_url: window.location.href,
  page_path: "/school/abbotsford-highstreet/",
  tracking_source: "helper_plugin",
  click_url: "https://cefamain.kinsta.cloud/submit-an-inquiry-today/?location=abbotsford-highstreet",
  click_text: "Inquire Now",
  cta_id: "school_parent_inquiry_cta_click",
  cta_location: "hero",
  lead_intent: "inquire_now",
  form_id: "4",
  form_family: "parent_inquiry",
  school_selected_slug: "abbotsford-highstreet"
});
```

These are diagnostic/reporting events. They should go to GA4/BigQuery reporting first and should stay out of Google Ads bidding at launch unless CEFA explicitly decides otherwise.

## Attribution Persistence

The plugin ports the old parent-site attribution-cookie logic into the CEFA-owned tracking bridge:

- `cefa_first_landing_page` and `cefa_first_referrer` are set once for 90 days.
- `cefa_last_utm_source`, `cefa_last_utm_medium`, `cefa_last_utm_campaign`, `cefa_last_utm_term`, and `cefa_last_utm_content` update only when matching URL parameters are present.
- `cefa_last_gclid`, `cefa_last_gbraid`, `cefa_last_wbraid`, `cefa_last_fbclid`, and `cefa_last_msclkid` update only when matching click-ID parameters are present.
- The browser writes the values into new Form 4 fields `35` through `46` when the fields are empty.
- A server-side `gform_pre_submission_4` fallback backfills the same fields from cookies before Gravity Forms saves the entry.
- Fields `33` and `34` are intentionally not modified because the redesign uses them for location/location-title values.

For Franchise Canada, the plugin keeps GAConnector as the attribution source for now:

- It reads existing hidden fields `14` through `30`.
- It does not overwrite GAConnector-populated values.
- If those fields remain empty after real submission testing, a later version can add a narrow missing-value backfill.

## Install On Staging

1. Create a ZIP:

   ```bash
   mkdir -p dist
   git archive --format=zip --output=dist/cefa-conversion-tracking.zip HEAD
   ```

2. Upload the ZIP in WordPress Admin under `Plugins > Add New > Upload Plugin`.
3. Activate `CEFA Conversion Tracking`.
4. Keep the Gravity Forms Google Analytics Add-On event unmapped in GTM if this helper plugin is the final event source.

## Acceptance Tests

- Successful Form 4 submission creates a Gravity Forms entry and exactly one `school_inquiry_submit` in `dataLayer`.
- `dataLayer.event_id` equals entry field `32.4`.
- Fields `32.1` through `32.7` appear as clean separate parameters.
- Attribution fields `35` through `46` are saved as clean separate values when UTM/click-ID parameters are present.
- Invalid form submission fires no final conversion event.
- Direct `/thank-you/?location=<slug>&inquiry=true` visit without a plugin token fires no final conversion event.
- Thank-you page reload does not fire a second conversion.
- GA add-on / GTM POC events are not mapped as duplicate final conversions.

## Operational Docs

- [Live migration read-only audit, 2026-04-30](docs/live-migration-readonly-audit-2026-04-30.md)
- [Parent production cutover checklist](docs/parent-production-cutover-checklist.md)
- [Cross-property measurement boundaries](docs/cross-property-measurement-boundaries.md)
- [Franchise Canada Phase 1 tracking plan](docs/franchise-canada-phase1/README.md)
- [GPT Pro review handoff for franchise Meta transition](docs/gpt-pro-review-franchise-meta-transition-2026-04-28.md)
- [Reviewed franchise transition plan](docs/franchise-transition-reviewed-plan-2026-04-28.md)
- [GPT Pro franchise transition final pack](docs/franchise-transition-final-pack-v1/00-executive-summary-and-final-decision.md)

## Development

Install dev dependencies:

```bash
composer install
```

Run checks:

```bash
composer lint:php
composer phpcs
node --check assets/js/cefa-conversion-tracking.js
```

## Phase Roadmap

- Phase 1A: clean browser/form event identity and staging signoff.
- Phase 1B: attribution hardening, collector audit path, and Meta CAPI using shared `event_id`.
- Phase 2: custom-domain sGTM, broader server-side routing, and BigQuery reporting.
- Franchise Canada: audit after parent stabilization, contain GTM by hostname, stabilize active Meta campaigns inside the current shared dataset if needed, then test and migrate to a separate franchise Canada dataset.
- Franchise USA: audit separately and use separate destination boundaries by default before serious production optimization.
