# Parent Production Cutover Checklist

Last updated: 2026-04-28

This checklist holds the parent-site conversion-tracking state until the new parent website moves from staging to production.

## Current Staging Baseline

- Staging site: `https://cefamain.kinsta.cloud`
- Current staging inquiry route: `/submit-an-inquiry-today/?location=<school-slug>`
- WordPress helper plugin: `CEFA Conversion Tracking`
- Canonical website event: `school_inquiry_submit`
- GA4 event mapped in GTM: `generate_lead`
- Staging GTM container: `GTM-NZ6N7WNC`
- Final conversion source: helper-plugin dataLayer event, not Gravity Forms Google Analytics Add-On

## GA4 Property State

The Phase 1A custom definitions were created in:

- GA4 account: `accounts/17532283`
- Account name in UI: `CEFA`
- Property: `properties/267558140`
- Property name in UI: `Main Site - GA4`
- UI breadcrumb: `CEFA > cefa.ca > Main Site - GA4`
- UI path: `Admin > Data display > Custom definitions > Custom dimensions`

Registered event-scoped custom dimensions:

- `form_id`
- `form_family`
- `lead_type`
- `lead_intent`
- `school_selected_id`
- `school_selected_slug`
- `school_selected_name`
- `program_id`
- `program_name`
- `days_per_week`
- `tracking_source`
- `page_type`
- `cta_id`
- `cta_location`

Existing GA4 key events:

- `generate_lead`
- `inquiry_click`
- `email_click`
- `phone_click`
- `find_a_school_click`
- `purchase`

Nothing was deleted from GA4 during the staging setup.

## Do Not Change Before Production Signal

- Do not archive old GA4 custom dimensions while the current live site may still use them.
- Do not remove existing GA4 key events until Google Ads imports and historical reports are reviewed.
- Do not re-enable Gravity Forms Google Analytics Add-On as a second final conversion source.
- Do not let thank-you pageviews become the final lead conversion source again.

## Production Cutover Tasks

- [ ] Confirm final production parent domain and route paths.
- [ ] Confirm final inquiry route replacing staging `/submit-an-inquiry-today/`.
- [ ] Confirm final thank-you route and query-string behavior.
- [ ] Confirm Form 4 remains the parent inquiry form.
- [ ] Confirm Field 32 subfields remain stable from `32.1` through `32.7`.
- [ ] Confirm attribution fields remain stable from `35` through `46`.
- [ ] Confirm `school_inquiry_submit` fires only after confirmed Form 4 success.
- [ ] Confirm browser `event_id` matches Gravity Forms field `32.4`.
- [ ] Confirm direct thank-you visits and reloads do not fire false conversions.
- [ ] Confirm invalid Form 4 submissions do not fire `school_inquiry_submit`.
- [ ] Confirm GTM maps `school_inquiry_submit` to GA4 `generate_lead`.
- [ ] Confirm GTM passes the registered GA4 parameters listed above.
- [ ] Confirm production Google Ads conversion action and label.
- [ ] Confirm parent Meta dataset/pixel and final event name.
- [ ] Confirm micro-conversions stay out of bidding unless explicitly approved.

## Production QA Scenarios

- [ ] School page inquiry path with `location=<school-slug>`.
- [ ] Find a School path into inquiry flow.
- [ ] Direct inquiry URL from Google Business Profile or other external placements.
- [ ] Paid search URL with UTM, `gclid`, `gbraid`, and `wbraid`.
- [ ] Paid social URL with UTM and `fbclid`.
- [ ] Microsoft Ads URL with UTM and `msclkid`.
- [ ] Invalid form submit.
- [ ] Direct thank-you URL visit.
- [ ] Thank-you page reload.
- [ ] Mobile browser submission.

## After Production Is Stable

- [ ] Review old GA4 custom dimensions and archive only if no longer needed.
- [ ] Review old GA4 key events and remove key-event status only if no longer needed.
- [ ] Archive old GTM tags/triggers/variables that are proven obsolete.
- [ ] Confirm Google Ads and Meta use only the intended final conversion signals.
- [ ] Begin next-phase server-side collector, Meta CAPI, sGTM, and BigQuery work.
