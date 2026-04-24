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
