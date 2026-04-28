# Parent Production Cutover Blueprint

## Final parent boundary

Keep:

- `CEFA Conversion Tracking` helper plugin
- `school_inquiry_submit`
- GTM mapping layer
- GA4 `generate_lead`
- parent micro-conversions as reporting diagnostics
- Form 4 field contract
- attribution hidden fields 35–46

Do not re-open parent architecture unless a production cutover test fails.

## Parent production checklist

Before moving parent staging to production:

1. Confirm final production domain and routes.
2. Confirm final inquiry route replacing staging `/submit-an-inquiry-today/`.
3. Confirm final thank-you route and query behavior.
4. Confirm Form 4 remains the parent inquiry form.
5. Confirm Field 32 subfields remain stable:
   - `32.1` selected school UUID
   - `32.2` program ID
   - `32.3` days per week
   - `32.4` event ID
   - `32.5` school slug
   - `32.6` school name
   - `32.7` program name
6. Confirm attribution fields `35` through `46` remain stable.
7. Confirm `school_inquiry_submit` fires only after confirmed Form 4 success.
8. Confirm browser `event_id` matches Gravity Forms field `32.4`.
9. Confirm direct thank-you visits do not fire conversions.
10. Confirm reloads do not duplicate conversions.
11. Confirm invalid Form 4 submissions do not fire `school_inquiry_submit`.
12. Confirm GTM maps `school_inquiry_submit` to GA4 `generate_lead`.
13. Confirm production Google Ads conversion action and label.
14. Confirm parent Meta dataset/pixel strategy before Meta tag mapping.
15. Confirm micro-conversions stay out of Google Ads bidding unless explicitly approved.

## Parent GTM cleanup timing

Do not delete old tags, variables, or GA4 custom dimensions until after production cutover is stable.

Recommended after cutover:

- Archive obsolete thank-you-page conversion tags.
- Archive malformed Gravity Forms Add-On event tags.
- Archive old POC tags.
- Keep a rollback export of pre-cleanup and post-cleanup GTM containers.
