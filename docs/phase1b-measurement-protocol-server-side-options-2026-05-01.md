# Phase 1B Measurement Protocol And Server-Side Options

Last updated: 2026-05-01

## Current State

Parent `cefa.ca` currently uses the CEFA Conversion Tracking plugin as the website-side source of truth for Form `4`.

The current production path is:

1. Gravity Forms saves a valid Form `4` submission.
2. The CEFA plugin confirms the saved entry and creates a one-time thank-you token.
3. The thank-you page fetches the confirmed payload.
4. The browser pushes `school_inquiry_submit` into `window.dataLayer`.
5. GTM maps `school_inquiry_submit` to GA4 `generate_lead`, Google Ads, Meta, and supporting destinations.

Live GA4 BigQuery export has confirmed that `generate_lead` rows from the helper-plugin path include:

- `tracking_source=helper_plugin`
- `form_id=4`
- `form_family=parent_inquiry`
- `inquiry_success=true`
- `event_id`
- `school_selected_id`
- `school_selected_slug`
- `school_selected_name`
- `program_id`
- `program_name`
- `days_per_week`

Failed validation does not emit `generate_lead`. It emits the diagnostic micro-event `validation_error`.

## Gravity Forms Measurement Protocol Capability

The Gravity Forms Google Analytics Add-On can use Google Measurement Protocol as a connection type and can trigger feeds on form submission. Gravity Forms feed settings allow event parameters to be mapped from form fields. This means hidden fields can be sent, subject to GA4 Measurement Protocol limits.

This is useful because the request is made from the WordPress/Gravity Forms side after submission, not from the visitor browser. It can therefore create a server-side GA4 signal for confirmed submissions.

Important limits and constraints:

- GA4 Measurement Protocol is intended to supplement gtag/GTM collection, not replace it.
- GA4 Measurement Protocol still works best when tied to browser tagging using `client_id` and, ideally, `session_id`.
- GA4 Measurement Protocol allows up to 25 event parameters per event.
- Standard GA4 parameter values are limited to 100 characters.
- Measurement Protocol collection can return HTTP success even when a payload is malformed or not useful for reporting, so validation and reporting checks are required.
- The Gravity Forms add-on gives less control than CEFA-owned plugin code over duplicate guards, event naming, log shape, retry behavior, and future collector/CAPI/sGTM alignment.

## Do Not Activate As A Second Primary Conversion Source

Do not enable Gravity Forms Measurement Protocol to send GA4 `generate_lead` while the browser/GTM `generate_lead` remains active.

That would create two possible GA4 lead events for one form submission:

- browser/GTM `generate_lead` from `school_inquiry_submit`
- server/Gravity Forms Measurement Protocol `generate_lead`

GA4 should not be treated as safely deduping lead events only because an `event_id` parameter exists. CEFA should control deduplication at the implementation layer.

## Recommended Exploration Path

Use Measurement Protocol as an audit-only Phase 1B signal first.

Recommended first event:

```text
school_inquiry_submit_server_audit
```

This event should not be marked as a GA4 key event and should not be imported into Google Ads.

Minimum audit parameters:

- `event_id`
- `form_id`
- `form_family`
- `entry_id`
- `tracking_source`
- `server_transport`
- `school_selected_id`
- `school_selected_slug`
- `school_selected_name`
- `program_id`
- `program_name`
- `days_per_week`
- `utm_source`
- `utm_medium`
- `utm_campaign`
- `utm_term`
- `utm_content`
- `gclid`
- `gbraid`
- `wbraid`
- `first_landing_page`
- `first_referrer`

Because Measurement Protocol has a 25-parameter limit, do not send every form field to GA4. Send only non-PII conversion metadata and attribution fields needed for reporting/QA. Parent/guardian names, email, phone, notes, child details, and other PII must not be sent to GA4 event parameters.

## Requirements To Test Gravity Forms Add-On MP Safely

If testing the Gravity Forms Google Analytics Add-On Measurement Protocol path:

1. Keep the CEFA browser/GTM `generate_lead` path active.
2. Configure the Gravity Forms GA add-on with Measurement Protocol credentials for the correct GA4 stream.
3. Create a Form `4` feed that sends `school_inquiry_submit_server_audit`, not `generate_lead`.
4. Map only approved non-PII fields and hidden fields.
5. Include a parameter such as `server_transport=gravity_forms_mp`.
6. Include the same Form `4` `event_id` from field `32.4`.
7. Confirm the add-on sends with the same client/session context where possible.
8. Submit a controlled test with a unique UTM campaign value.
9. Verify no browser network request exists for `school_inquiry_submit_server_audit`.
10. Verify the event appears in GA4 BigQuery export with `server_transport=gravity_forms_mp`.
11. Compare the audit event against the browser `generate_lead` and the Gravity Forms entry by `event_id`.

Acceptance rule:

```text
one valid Form 4 entry
= one browser generate_lead
= zero or one server audit event
= matching event_id
= no extra GA4 key event
```

## How To Prove It Is Server-Side

Evidence should include all of the following:

- Browser DevTools network does not show a client-side request for `school_inquiry_submit_server_audit`.
- Gravity Forms / WordPress server logs show the add-on or custom code making the outbound Measurement Protocol request.
- GA4 BigQuery export shows `event_name=school_inquiry_submit_server_audit`.
- The audit event includes `server_transport=gravity_forms_mp` or `server_transport=cefa_plugin_mp`.
- The audit event shares the same `event_id` as the browser `generate_lead` and Gravity Forms field `32.4`.
- The audit event appears even if the browser thank-you page is not allowed to send the client-side event during a controlled server-side test.

If CEFA-owned plugin code is used instead of the Gravity Forms add-on, also validate the payload against the Measurement Protocol validation endpoint before production collection.

## Preferred Long-Term Direction

The Gravity Forms add-on is acceptable for exploration and audit-only testing.

For the final server-side conversion layer, the preferred direction remains CEFA-owned plugin or collector code because it gives stronger control over:

- duplicate prevention
- event naming
- payload limits
- validation logging
- retry behavior
- server-side Meta CAPI
- future server-side GTM
- future BigQuery collector persistence

Recommended future path:

1. Test Gravity Forms MP as `school_inquiry_submit_server_audit`.
2. Compare parity with browser `generate_lead`.
3. If useful, implement CEFA-owned Measurement Protocol sender in the helper plugin or collector.
4. Keep browser/GTM `generate_lead` primary until server parity is proven.
5. Only move GA4 `generate_lead` to server-side after disabling the browser GA4 `generate_lead` tag.

## REST API And Webhooks

Gravity Forms REST API v2 and Webhooks are useful for future server-side architecture, but they solve different problems.

REST API v2:

- Useful for pulling forms/entries into a collector, QA process, or data warehouse.
- Requires REST authentication.
- Useful for reconciliation and backfills.
- Not the preferred live conversion trigger by itself because it needs an external polling or orchestration layer.

Gravity Forms Webhooks:

- Useful for pushing a saved entry to a CEFA collector endpoint after form submission.
- Can send all fields or selected fields in JSON.
- Better aligned with the future collector / CAPI / sGTM roadmap than sending directly to GA4 from the Gravity Forms add-on.
- Should point to a CEFA-controlled endpoint, not directly to every ad platform.

Future collector path:

```text
Gravity Forms confirmed submission
-> CEFA plugin/webhook sends signed payload to CEFA collector
-> collector validates and stores durable event
-> collector dispatches GA4 MP, Meta CAPI, Google Ads enhanced conversions/offline import, LinkedIn CAPI/offline, and BigQuery
```

This is the cleaner long-term model, but it is not required before Phase 1A/Canada Phase 1 browser tracking is stable.

## Current Recommendation

Do not switch primary GA4 lead tracking to Gravity Forms Measurement Protocol now.

Do test Measurement Protocol as an audit-only server-side event if CEFA wants an additional server confirmation layer before building the full collector.

Do not let Gravity Forms Measurement Protocol and GTM both send GA4 `generate_lead` for the same submission.
