# CEFA Conversion Tracking

Lightweight WordPress plugin for CEFA parent-site conversion tracking.

This plugin emits clean CEFA parent-site `dataLayer` events for the confirmed Form 4 inquiry conversion and the Phase 1A browser micro-conversions.

It does not replace Gravity Forms, CEFA School Manager, Field 32 UI, location sync, tracking cookies, KinderTales, GTM, or platform tags.

## What It Owns

- Ensures Form 4 field `32.4` has a unique submission-scoped `event_id`.
- Uses the saved Gravity Forms entry as the source of truth.
- Creates a short-lived one-time thank-you-page token after successful submission.
- Pushes one clean `school_inquiry_submit` event into `window.dataLayer`.
- Prevents direct thank-you-page false positives and reload duplicates.
- Pushes plugin-owned micro-conversion events for inquiry CTA clicks, Find a School clicks, phone clicks, email clicks, Form 4 starts, submit attempts, and validation errors.
- Uses GA4-style structured metadata instead of legacy Universal Analytics event category/action/label fields.

## What It Does Not Own

- Form 4 UI.
- CEFA School Manager school/program/day behavior.
- Field 32 structure.
- School locking.
- Location sync.
- Attribution cookies.
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
- Invalid form submission fires no final conversion event.
- Direct `/thank-you/?location=<slug>&inquiry=true` visit without a plugin token fires no final conversion event.
- Thank-you page reload does not fire a second conversion.
- GA add-on / GTM POC events are not mapped as duplicate final conversions.

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
- Phase 1B: collector audit path and Meta CAPI using shared `event_id`.
- Phase 2: custom-domain sGTM, broader server-side routing, and BigQuery reporting.
