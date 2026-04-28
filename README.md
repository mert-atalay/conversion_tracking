# CEFA Conversion Tracking

Lightweight WordPress plugin for CEFA parent-site conversion tracking.

This plugin emits clean CEFA parent-site `dataLayer` events for the confirmed Form 4 inquiry conversion, Phase 1A browser micro-conversions, and Phase 1B attribution persistence.

It does not replace Gravity Forms, CEFA School Manager, Field 32 UI, location sync, KinderTales, GTM, or platform tags.

## What It Owns

- Ensures Form 4 field `32.4` has a unique submission-scoped `event_id`.
- Uses the saved Gravity Forms entry as the source of truth.
- Creates a short-lived one-time thank-you-page token after successful submission.
- Pushes one clean `school_inquiry_submit` event into `window.dataLayer`.
- Prevents direct thank-you-page false positives and reload duplicates.
- Pushes plugin-owned micro-conversion events for inquiry CTA clicks, Find a School clicks, phone clicks, email clicks, Form 4 starts, submit attempts, and validation errors.
- Stores first-touch and last-touch attribution in the same first-party cookie pattern used by the old parent site.
- Backfills Form 4 attribution fields `35` through `46` before submission if they are empty.
- Uses GA4-style structured metadata instead of legacy Universal Analytics event category/action/label fields.

## What It Does Not Own

- Form 4 UI.
- CEFA School Manager school/program/day behavior.
- Field 32 structure.
- School locking.
- Location sync.
- School Manager location cookies/session state.
- KinderTales/business submission delivery.
- GA4, Google Ads, Meta, CAPI, Measurement Protocol, collector, or sGTM outbound calls.

## Required Runtime

- WordPress `6.3+`.
- PHP `7.4+`.
- Gravity Forms with Form ID `4`.
- CEFA School Manager continuing to populate Form 4 field `32.*` values.

## DataLayer Contract

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

- [Parent production cutover checklist](docs/parent-production-cutover-checklist.md)
- [Cross-property measurement boundaries](docs/cross-property-measurement-boundaries.md)

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
- Franchise Canada: audit and implement after parent stabilization, with subdomain GTM containment.
- Franchise USA: audit and implement after franchise Canada, with separate destination boundaries.
