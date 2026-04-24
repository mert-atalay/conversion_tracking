# Event Flow And Event ID Lifecycle

## Event ID Rule

```text
event_id = unique per successful submission event
school_selected_id = school metadata
```

Never use school UUID or school slug as `event_id`.

## Preferred Phase 1A Flow

1. User opens the Form 4 page.
2. Existing CEFA School Manager resolves selected school/program/day.
3. Helper plugin ensures field `32.4` has an `event_id`.
4. User submits Form 4.
5. Gravity Forms validates and saves the entry.
6. Helper plugin creates a short-lived token from the saved entry.
7. Confirmed success redirects to the thank-you page or shows inline confirmation.
8. Helper plugin emits one clean `school_inquiry_submit`.
9. GTM maps `school_inquiry_submit` to GA4, Google Ads, and Meta destinations.

## Lifecycle

- Form render: generate browser UUID if `32.4` is empty.
- Submit attempt: preserve pending event state only; do not fire conversion.
- Confirmed success: use saved `32.4`, tokenized server payload, and one `dataLayer` push.
- Reload: consumed event IDs do not push again.
- Direct thank-you visit: no plugin token means no final conversion event.
