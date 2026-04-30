# Franchise Canada Open GPT Pro Questions

Last updated: 2026-04-30

Use this file if we want GPT Pro to review the remaining Canada franchise decisions before implementation.

## Context

The new Canada franchise staging site is not the old popup/Elementor flow. It uses page-based Gravity Forms:

- Form `1`: `Franchise Inquiry` on `/available-opportunities/franchising-inquiry/`
- Form `2`: `Site Inquiry` on `/partner-with-cefa/real-estate-partners/submit-a-site/` and `/partner-with-cefa/real-estate-partners/`
- Form `3`: `Newsletter`

The existing Canada franchise GTM container is `GTM-TPJGHFS`. It is still useful for IDs and legacy conversion examples, but the old conversion logic is based on old paths, Elementor form selectors, and thank-you/pageview triggers. The new build needs confirmed-success dataLayer events.

GAConnector is also active through the current runtime. The forms already have hidden attribution fields `14` through `30`. Runtime checks confirmed GAConnector scripts/cookies and `gclid` population into field `29`, but did not yet prove that `lc_*`, `fc_*`, or `GA_Client_ID` values are saved cleanly in real Gravity Forms entries.

## Questions

1. Should Canada franchise staging continue using the existing `GTM-TPJGHFS` container with strict hostname/workspace containment, or should we create a clean staging container and ask the agency/site owner to swap the snippet?

2. Given GAConnector is active but full hidden-field population is not yet proven, should the helper plugin only read saved fields `14` through `30`, or should it also backfill missing attribution values from URL parameters and approved first-party/GAConnector cookies?

3. For event identity, should the plugin add explicit hidden `ct_event_id` fields to Form `1` and Form `2`, or is Gravity Forms entry meta sufficient for Phase 1 browser/server parity?

4. Should Form `1` and Form `2` both map to GA4 `generate_lead` with different metadata, or should Form `2` also keep a distinct GA4 event name for real-estate/site-submission reporting?

5. During the Canada Meta transition, should both Form `1` and Form `2` send standard Meta `Lead` into the current shared dataset first, using custom conversion rules to separate franchise leads, while a separate dataset receives only parallel/test traffic?

6. If GAConnector remains the attribution source, what is the minimum evidence needed before launch: runtime hidden-field population, saved Gravity Forms entry fields, GA4 event parameters, or all three?

## Current Recommendation

Proceed with the GPT Pro hybrid boundary:

- Keep GAConnector as the existing attribution source unless real entry tests prove it is insufficient.
- Use a narrow CEFA helper plugin only for confirmed-success event identity, one-time token/duplicate guards, non-PII payload assembly, and optional approved attribution backfill.
- Keep GTM as the destination mapping layer.
- Keep Meta Canada in the shared dataset temporarily if active campaigns still depend on it, but create franchise-specific parameters and custom conversions.
- Keep CAPI and sGTM as later hardening phases after clean browser parity.
