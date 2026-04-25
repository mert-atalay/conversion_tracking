# Phase 1A Acceptance Tests

Final signoff condition:

```text
One successful Form 4 submission
-> one school_inquiry_submit event
-> same event_id in dataLayer and Gravity Forms field 32.4
-> clean separate parameters
-> no false positives
-> no duplicate fires
```

## Required Tests

- Real submission: Gravity Forms entry exists and browser dataLayer contains one final `school_inquiry_submit`.
- Event ID match: `dataLayer.event_id` equals entry `32.4`.
- Clean parameters: `32.1` through `32.7` are separate values.
- Failed validation: no final conversion fires.
- Direct thank-you visit: no final conversion fires without plugin token.
- Reload: no second conversion fires.
- Duplicate source: GA add-on / GTM POC events are not mapped as final platform conversions if helper plugin is final.

## Micro-Conversion Tests

- Inquiry CTA click: clicking a normal same-window inquiry CTA pushes one `parent_inquiry_cta_click` before navigation.
- Find a School click: clicking a `/find-a-school/` link pushes `find_a_school_click`.
- Phone click: clicking a `tel:` link pushes `phone_click`.
- Email click: clicking a `mailto:` link pushes `email_click`.
- Form start: the first non-hidden Form 4 interaction pushes one `form_start` per form event ID/session.
- Submit attempt: a Form 4 submit attempt pushes `form_submit_click`; this remains diagnostic and is not the final conversion.
- Validation error: a failed validation render pushes `validation_error`; it must not push `school_inquiry_submit`.
- GTM mapping: GA4 receives these as event-name-plus-parameter events, not as Universal Analytics category/action/label fields.
