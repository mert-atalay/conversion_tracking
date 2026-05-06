# Franchise Canada Phase 1 Tracking Plan

Last updated: 2026-05-05

This folder is the working implementation package for the new Canada franchise website tracking rollout.

Scope:
- Current/live Canada franchise property: `https://franchise.cefa.ca`
- Former Canada franchise staging property: `https://cefafranchise.kinsta.cloud`
- GTM account: `6004334435`
- Current Canada franchise GTM container: `GTM-TPJGHFS` / container `48104535`
- GA4 property: `259747921` / `CEFA Franchise`
- Primary website forms:
  - Gravity Forms Form `1` / `Franchise Inquiry`
  - Gravity Forms Form `2` / `Site Inquiry`
  - Gravity Forms Form `3` / `Newsletter`

## Current Decision

The website is now live on the original domain. Treat this folder as the implementation plan and prior evidence, but use the live-domain status note as the current checkpoint before configuring GTM/GA4.

Start Canada franchise as an audit-first Phase 1 build, not a blind copy of the old GTM container.

Latest live-domain checkpoint:

- [Live conversion tracking status, 2026-05-01](../live-conversion-tracking-status-2026-05-01.md)

Current live result:

- Forms `1` and `2` are visible on the expected live paths.
- `GTM-TPJGHFS` is visible.
- GAConnector scripts and hidden fields `14` through `30` are visible.
- The WPCode fallback bridge is visible on the Form `1` and Form `2` paths.
- Controlled Form `1` and Form `2` submissions proved the confirmed-success dataLayer events and `event_id` entry-meta join.
- GTM Version `54` is live. It keeps the website event `franchise_inquiry_submit` neutral, but maps the final Form `1` submit to the existing learning/primary destinations: Meta `Fr Application Submit` on dataset `918227085392601` and Google Ads `fr_application_submit` using `AW-11088792613/cys-CIHslY4YEKWYxqcp`.
- GTM Version `54` also disables the old `/thank-you` pageview application-submit trigger by changing trigger `38` to `Legacy DISABLED - Fr Application Submit_ollo`, and pauses the old pageview Meta tag `51`.
- The secondary Google Ads `fr_inquiry_submit` tag is paused so Form `1` does not send both the old primary application action and the newer inquiry action as duplicate final conversions.
- GA4 Data API has reported at least one processed `generate_lead` on host `franchise.cefa.ca`, and the low-cardinality helper payload custom dimensions are registered.
- 2026-05-03 GA4 Data API refresh reported `4` processed `generate_lead` rows on host `franchise.cefa.ca`, including `1` helper-plugin row with franchise Canada metadata.
- Google Ads primary/secondary direction is resolved for continuity: preserve existing primary `fr_application_submit`; keep `fr_inquiry_submit`, `fr_site_form_submit`, and imported `generate_lead (GA4)` secondary unless a later paid-media decision changes that.
- Post-Version-54 controlled browser QA passed for the core continuity path: Form `1` pushed one `franchise_inquiry_submit`, GTM dispatched `cefa_franchise_inquiry_dispatch`, Google Ads fired the existing primary `fr_application_submit` label `AW-11088792613/cys-CIHslY4YEKWYxqcp`, GA4 fired `generate_lead`, and the secondary `fr_inquiry_submit` label `MfYYCITslY4YEKWYxqcp` was not observed. The Meta `Fr Application Submit` browser call executed; Events Manager receipt still needs UI/platform confirmation after processing delay.

Use the old Canada GTM container as a reference only. The old container already contains useful IDs and micro-conversion examples, but it is built around old paths, old Elementor form selectors, and thank-you/pageview logic. The new staging site uses Gravity Forms and different page paths.

GAConnector is already active through the current GTM/runtime and the new forms already include attribution hidden fields. The Phase 1 build should not replace GAConnector by default. It should verify whether GAConnector actually writes clean values into the saved Gravity Forms entries, then read those values into the final dataLayer payload. If the hidden fields remain empty, CEFA needs a narrow decision on whether the helper plugin should backfill from URL parameters and GAConnector/first-party cookies.

## Build Direction

For Phase 1 browser tracking:
- Keep website events neutral.
- Use GTM as the destination mapping layer.
- Keep platform event names such as GA4 `generate_lead` and Meta `Lead` inside GTM.
- Use a narrow helper-plugin module if we need confirmed-success dataLayer events with event IDs, duplicate guards, and clean form metadata.
- Do not let the helper plugin replace Gravity Forms, CEFA Franchise API, Synuma/SiteZeus delivery, notifications, or form UI logic.

## Files

- [Current audit](./01-current-audit-2026-04-29.md)
- [Event taxonomy and dataLayer contracts](./02-event-taxonomy-and-datalayer-contract.md)
- [GTM build plan](./03-gtm-build-plan.md)
- [Helper plugin plan](./04-helper-plugin-plan.md)
- [QA and cutover checklist](./05-qa-and-cutover-checklist.md)
- [Open GPT Pro questions](./06-open-gpt-pro-questions.md)
- [Content freeze reset note](./07-content-freeze-reset-note-2026-04-30.md)
- [Post-Version-54 Application Submit QA](./08-post-v54-application-submit-qa-2026-05-05.md)
