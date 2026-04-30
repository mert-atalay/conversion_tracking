# Franchise Canada Helper Plugin Plan

Last updated: 2026-04-29

## Decision

A helper-plugin module is recommended for Canada franchise before final conversion mapping.

Reason:

- GTM alone can track click URLs, Gravity Forms selectors, and thank-you pages.
- GTM alone cannot reliably prove a confirmed successful Gravity Forms submission, share the same event identity with the saved entry, prevent direct thank-you false positives, and expose clean saved form metadata.
- The parent Phase 1A pattern already solved this with a narrow helper-plugin bridge.

## Plugin Boundary

The plugin may own:

- submission-scoped `event_id`
- short-lived success token
- one final dataLayer event per confirmed successful submission
- duplicate guards
- direct thank-you false-positive guards
- attribution cookie persistence and hidden-field population if current hidden fields are not already populated reliably
- non-PII dataLayer payload assembly

The plugin must not own:

- Gravity Forms form UI
- custom `cefa_location_select` business logic
- CEFA Franchise API CRM delivery
- Synuma/SiteZeus routing
- email notifications
- page/component rendering
- GA4, Google Ads, Meta, CAPI, collector, or sGTM outbound delivery in Phase 1

## Forms To Support

Form `1`:

- Form family: `franchise_inquiry`
- Final event: `franchise_inquiry_submit`
- Lead type: `franchise_lead`
- Confirmation page: `Submit an Inquiry - Thank You` / page ID `633`

Form `2`:

- Form family: `site_inquiry`
- Final event: `real_estate_site_submit`
- Lead type: `real_estate_lead`
- Confirmation page: `Submit a Site - Thank You` / page ID `636`

Form `3`:

- Form family: `newsletter`
- Treat as secondary only.
- Do not include in primary lead conversion mapping unless explicitly approved.

## Event ID Storage

Preferred:

- Add or detect a hidden field with input name `ct_event_id` for each supported form.
- Populate it before Gravity Forms saves the entry.
- Use the same value in the final dataLayer payload.

Fallback if no hidden field is approved:

- Store the event ID as Gravity Forms entry meta and in the one-time success payload.
- This is acceptable for browser/entry debugging, but less ideal for external webhook/server-side matching.

Do not use selected location, page slug, form ID, email, phone, or any CRM ID as `event_id`.

## Confirmation Flow

Use Gravity Forms hooks:

- `gform_pre_submission_1`
- `gform_pre_submission_2`
- `gform_confirmation_1`
- `gform_confirmation_2`

Expected flow:

1. Generate `event_id` if missing.
2. Ensure attribution fields are present or backfilled from first-party cookies.
3. After confirmed submission, build payload from the saved entry.
4. Store payload in a short-lived transient keyed by a one-time token.
5. Add token to the confirmation page URL or pass it through a safe handoff method.
6. Frontend JS consumes token once and pushes the final dataLayer event.
7. Duplicate guard blocks reloads and repeated token reads.

## Franchise Module Configuration

The existing plugin should become configuration-driven instead of hardcoding parent Form 4 only.

Suggested config shape:

```php
[
    'franchise_ca' => [
        'hostnames' => [
            'cefafranchise.kinsta.cloud',
            'franchise.cefa.ca',
        ],
        'forms' => [
            1 => [
                'event_name'  => 'franchise_inquiry_submit',
                'form_family' => 'franchise_inquiry',
                'lead_type'   => 'franchise_lead',
                'lead_intent' => 'franchise_inquiry',
            ],
            2 => [
                'event_name'  => 'real_estate_site_submit',
                'form_family' => 'site_inquiry',
                'lead_type'   => 'real_estate_lead',
                'lead_intent' => 'submit_a_site',
            ],
        ],
    ],
]
```

## Acceptance Criteria

- Successful Form 1 submission creates exactly one `franchise_inquiry_submit`.
- Successful Form 2 submission creates exactly one `real_estate_site_submit`.
- `event_id` is unique per successful submission.
- Reloading the thank-you page does not fire the event again.
- Direct thank-you page visits without a valid token do not fire a primary event.
- Invalid form submissions do not fire a primary event.
- PII is not pushed into dataLayer.
- Attribution values are included only from approved hidden fields/cookies.

