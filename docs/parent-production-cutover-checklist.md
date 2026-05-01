# Parent Production Cutover Checklist

Last updated: 2026-05-01

This checklist records the parent-site `cefa.ca` conversion-tracking state after the new website moved to production.

## Current Live Baseline

- Live site: `https://cefa.ca`
- Current live inquiry route: `/submit-an-inquiry-today/?location=<school-slug>`
- WordPress helper plugin: `CEFA Conversion Tracking`
- Canonical website event: `school_inquiry_submit`
- GA4 event mapped in GTM: `generate_lead`
- Live GTM container: `GTM-NZ6N7WNC`
- Old parent GTM container: `GTM-PPV9ZRZ`, reference-only/not present in sampled live HTML
- Final conversion source: helper-plugin dataLayer event, not Gravity Forms Google Analytics Add-On

Live check on `2026-05-01` confirmed:

- `https://cefa.ca/submit-an-inquiry-today/?location=abbotsford-highstreet` renders `GTM-NZ6N7WNC`.
- The sampled live inquiry page does not render `GTM-PPV9ZRZ`.
- The sampled live inquiry page includes `cefa-conversion-tracking`, `school_inquiry_submit`, `validation_error`, and the one-time tracking-token logic.
- The public `GTM-NZ6N7WNC` container includes `school_inquiry_submit`, `generate_lead`, `G-T65G018LYB`, `AW-802334988`, and Meta pixel `918227085392601`.

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

Verified on `2026-05-01` through the GA4 Admin API:

- `generate_lead` is a key event.
- `validation_error` is not a key event.
- GA4 property `267558140` is linked to Google Ads customer `4159217891`.

Nothing was deleted from GA4 during the staging setup.

## Do Not Change Before Production Signal

- Do not archive old GA4 custom dimensions while the current live site may still use them.
- Do not remove existing GA4 key events until Google Ads imports and historical reports are reviewed.
- Do not re-enable Gravity Forms Google Analytics Add-On as a second final conversion source.
- Do not let thank-you pageviews become the final lead conversion source again.

## Production Cutover Tasks

- [x] Confirm final production parent domain and route paths.
- [x] Confirm final inquiry route replacing staging `/submit-an-inquiry-today/`.
- [x] Confirm final thank-you route and query-string behavior.
- [x] Confirm Form 4 remains the parent inquiry form.
- [x] Confirm Field 32 subfields remain stable from `32.1` through `32.7`.
- [x] Confirm attribution fields remain stable from `35` through `46`.
- [x] Confirm `school_inquiry_submit` fires only after confirmed Form 4 success.
- [x] Confirm browser `event_id` matches Gravity Forms field `32.4`.
- [x] Confirm direct thank-you visits and reloads do not fire false conversions.
- [x] Confirm invalid Form 4 submissions do not fire `school_inquiry_submit`.
- [x] Confirm GTM maps `school_inquiry_submit` to GA4 `generate_lead`.
- [x] Confirm GTM passes the registered GA4 parameters listed above.
- [x] Confirm production Google Ads conversion ID and label are present in the active GTM container.
- [x] Confirm parent Meta pixel and final event are present in the active GTM container.
- [x] Confirm micro-conversions stay out of Google Ads bidding tags in the active GTM container.

Still needs platform-owner confirmation:

- [ ] Confirm Google Ads conversion action primary/secondary status in Ads UI/API before bidding signoff.
- [ ] Confirm Meta Events Manager custom conversion / optimization-event status.

## Production QA Scenarios

- [x] School page inquiry path with `location=<school-slug>`.
- [x] Find a School path into inquiry flow.
- [x] Direct inquiry URL from Google Business Profile or other external placements.
- [x] Paid search URL with UTM, `gclid`, `gbraid`, and `wbraid`.
- [x] Paid social URL with UTM and `fbclid`.
- [x] Microsoft Ads URL with UTM and `msclkid`.
- [x] Invalid form submit.
- [x] Direct thank-you URL visit.
- [x] Thank-you page reload.
- [ ] Mobile browser submission.

GA4 BigQuery export check on `2026-05-01` for the last 7 days showed:

- `41` helper-plugin parent `generate_lead` events with `form_family=parent_inquiry`, `form_id=4`, and `inquiry_success=true`.
- `50` helper-plugin `validation_error` events with `form_family=parent_inquiry` and `form_id=4`.
- `0` duplicate helper-plugin `generate_lead` event IDs.
- Legacy/non-helper `generate_lead` rows also exist historically in the same property, mostly old thank-you URL patterns without `event_id` or `tracking_source`. Current sampled live HTML only loads `GTM-NZ6N7WNC`, not the old parent GTM container.

## After Production Is Stable

- [ ] Review old GA4 custom dimensions and archive only if no longer needed.
- [ ] Review old GA4 key events and remove key-event status only if no longer needed.
- [ ] Archive old GTM tags/triggers/variables that are proven obsolete.
- [ ] Confirm Google Ads and Meta use only the intended final conversion signals.
- [ ] Begin next-phase server-side collector, Meta CAPI, sGTM, and BigQuery work.
