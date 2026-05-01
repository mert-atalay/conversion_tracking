# Franchise Canada Content Freeze Reset Note

Last updated: 2026-04-30

## Why This Note Exists

The Franchise Canada website is now apparently in content freeze. That means the previous staging checks are useful as planning evidence, but the final implementation must be re-verified against the frozen website structure before deployment, GTM configuration, GA4 mapping, or platform conversion mapping.

Do not assume the earlier staging structure is still final until the frozen site is checked again.

## What Was Completed Today

### Plugin Work

The existing CEFA Conversion Tracking helper plugin was extended instead of creating a separate plugin.

Current plugin version:

- `0.4.0`

Latest implementation commit:

- `40d097c Add franchise Canada tracking bridge`

Packaged ZIP:

- `dist/cefa-conversion-tracking-0.4.0.zip`

Pull request:

- `https://github.com/mert-atalay/conversion_tracking/pull/1`

Implemented plugin behavior:

- Keeps parent Form `4` behavior intact.
- Adds hostname-scoped support for Franchise Canada:
  - `cefafranchise.kinsta.cloud`
  - `franchise.cefa.ca`
- Adds confirmed-success payload support for Franchise Canada Form `1`.
- Adds confirmed-success payload support for Franchise Canada Form `2`.
- Emits `franchise_inquiry_submit` for Form `1` after confirmed success.
- Emits `real_estate_site_submit` for Form `2` after confirmed success.
- Stores Franchise Canada `event_id` values in Gravity Forms entry meta because the current franchise forms do not have a dedicated event ID field.
- Reads existing GAConnector attribution hidden fields `14` through `30`.
- Does not overwrite GAConnector attribution fields.
- Does not send GA4, Google Ads, Meta, CAPI, Measurement Protocol, collector, or sGTM requests.

### Validation Completed Locally

Completed local checks:

- PHP syntax check passed for plugin PHP files outside `dist`.
- JavaScript syntax check passed for `assets/js/cefa-conversion-tracking.js`.
- Stubbed PHP smoke test confirmed the Franchise Canada hostname resolves to active forms `1` and `2`.
- Stubbed PHP smoke test confirmed Form `1` builds a `franchise_inquiry_submit` payload and reads GAConnector-style fields such as `lc_source` and `gclid`.
- Stubbed PHP smoke test confirmed the parent hostname still resolves to Form `4` and builds `school_inquiry_submit`.

Not completed:

- Plugin `0.4.0` has not been uploaded and activated on Franchise Canada staging.
- Real Form `1` and Form `2` submissions have not been tested with plugin `0.4.0`.
- Real Gravity Forms entries have not yet been checked for plugin entry meta event IDs.
- Real Gravity Forms entries have not yet been checked for GAConnector fields `14` through `30`.
- GTM/GA4 configuration has not yet been built against the new plugin events.

## Current Franchise Canada Website Knowledge Before Freeze Recheck

The prior staging audit found:

- Staging URL: `https://cefafranchise.kinsta.cloud`
- Live URL: `https://franchise.cefa.ca`
- Current GTM container: `GTM-TPJGHFS`
- GTM account: `6004334435`
- GTM container ID: `48104535`
- GA4 property: `259747921` / `CEFA Franchise`
- Form `1`: `Franchise Inquiry`
- Form `2`: `Site Inquiry`
- Form `3`: `Newsletter`
- Form `1` was found on `/available-opportunities/franchising-inquiry/`.
- Form `2` was found on `/partner-with-cefa/real-estate-partners/submit-a-site/` and `/partner-with-cefa/real-estate-partners/`.
- GAConnector scripts/cookies were active.
- Hidden attribution fields `14` through `30` existed.
- Test URL `gclid` populated field `29`.
- `lc_*`, `fc_*`, and `GA_Client_ID` values were not visibly proven in the runtime DOM before submit.

Because the site is now in content freeze, all of the above must be rechecked against the frozen website before implementation signoff.

## What Must Be Rebuilt Or Rechecked From Scratch

### Website Structure

Recheck the frozen Franchise Canada site for:

- final page URLs
- final Form `1`, Form `2`, and Form `3` presence
- final thank-you page flow
- whether forms are embedded, AJAX, iframe, or redirect-based
- whether page IDs or slugs changed
- whether `GTM-TPJGHFS` is still installed
- whether the staging site and live site still share the same GTM container

### Gravity Forms

Recheck:

- Form `1` field IDs and labels
- Form `2` field IDs and labels
- Form `1` and Form `2` confirmation behavior
- whether hidden attribution fields `14` through `30` still exist
- whether any new hidden field was added by the agency
- whether GAConnector values are saved into real entries

### Plugin

Before using the plugin as final source:

- Upload and activate `cefa-conversion-tracking-0.4.0.zip` on Franchise Canada staging.
- Submit Form `1` once with safe test values.
- Submit Form `2` once with safe test values.
- Confirm one `franchise_inquiry_submit` dataLayer event for Form `1`.
- Confirm one `real_estate_site_submit` dataLayer event for Form `2`.
- Confirm direct thank-you visits do not fire primary events.
- Confirm reloads do not duplicate events.
- Confirm event IDs are stored in Gravity Forms entry meta.
- Confirm no PII is pushed to dataLayer.
- Confirm GAConnector fields are read when populated and not overwritten.

### GTM And GA4

Do not configure final destination tags until the plugin events are verified on the frozen site.

After plugin verification:

- Create hostname-contained GTM triggers for `franchise_inquiry_submit` and `real_estate_site_submit`.
- Create dataLayer variables for the event payload fields.
- Map both primary events to GA4 reporting.
- Decide whether both events map to GA4 `generate_lead` with metadata or whether Form `2` keeps a separate GA4 event name.
- Keep Google Ads conversion tags disabled until conversion labels are confirmed.
- Keep Meta Lead mapping gated until the Canada dataset transition decision is confirmed.
- Keep micro-conversions out of Google Ads bidding at launch.

## Current Decision Boundary

Keep GAConnector attributes for now.

The plugin should not replace GAConnector attribution unless real post-freeze submission tests prove GAConnector is not saving usable values. If fields `14` through `30` remain empty, the next decision is whether to add a narrow plugin fallback for missing attribution values.

## Open Questions After Content Freeze

- Did the frozen site keep the same page paths and Gravity Forms IDs?
- Did Form `1` and Form `2` keep the same field IDs?
- Does GAConnector save `lc_*`, `fc_*`, `gclid`, and `GA_Client_ID` into real entries?
- Should event IDs remain entry meta for Franchise Canada, or should dedicated hidden fields be added before launch?
- Should staging continue using `GTM-TPJGHFS`, or should CEFA request a clean staging container/snippet for safer testing?
- Should Form `1` and Form `2` both map to GA4 `generate_lead`, separated by metadata?
- Should Canada Meta use the shared dataset temporarily with franchise-specific custom conversions before separate-dataset migration?

## Next Operator Instruction

Start from this order:

1. Re-audit the frozen Franchise Canada website structure.
2. Upload and activate plugin `0.4.0` on staging only.
3. Test Form `1` and Form `2` real submissions.
4. Read Gravity Forms entries to verify entry meta event IDs and GAConnector fields.
5. Only then configure GTM/GA4 against verified dataLayer events.
6. Do not enable Google Ads or Meta final conversions until dataset/label decisions are confirmed.
