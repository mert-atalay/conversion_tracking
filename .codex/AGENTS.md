# Codex-Local Franchise Tracking Guidance

This file is Codex-specific guidance for this checkout only. It does not replace repo-wide or parent project instructions.

## Ownership Boundary

This Codex thread owns only franchise conversion tracking:

- `franchise.cefa.ca`
- `franchisecefa.com`
- `www.franchisecefa.com`

Do not change parent `cefa.ca` implementation, parent GTM, parent GA4, parent form logic, or parent documentation unless the user explicitly reopens that scope.

Do not use unrelated WordPress MCP endpoints in this repo. Before using a WordPress MCP result for franchise tracking, confirm the target site URL is one of the franchise domains above. If the active WordPress MCP points anywhere else or exposes only non-Gravity-Forms tools, treat it as unavailable for franchise Gravity Forms work.

## Confirmed Reachability

As of the latest verified franchise tracking pass:

- GTM is reachable for franchise containers:
  - Canada: `GTM-TPJGHFS`
  - USA: `GTM-5LZMHBZL`
- GA4 connector can read franchise properties:
  - Canada: `259747921` / `CEFA Franchise`
  - USA: `519783092` / `CEFA Franchise - USA.`
- GA4 Admin/API work for franchise custom dimensions has been completed for the low-cardinality helper fields.
- Supermetrics can report Google Ads conversion-action performance for account `3820636025`, but the Supermetrics conversion-resource endpoint is not enough for direct Google Ads admin configuration.
- Direct Google Ads admin/API configuration still requires a local Google Ads API setup such as `~/.google-ads.yaml`, a developer token, and the correct login customer context.
- The currently active generic WordPress MCP tools must not be assumed to provide franchise Gravity Forms access unless the discovered site URL and abilities prove it.

## Tracking Structure

Gravity Forms saved entries are the submission source of truth for franchise forms.

The live browser/GTM path remains:

1. Gravity Forms successful submission.
2. WPCode/helper bridge emits one confirmed-success `dataLayer` event.
3. GTM maps the neutral helper event to platform destinations.

Franchise helper events:

- Form 1: `franchise_inquiry_submit`
- Form 2: `real_estate_site_submit`

Do not create duplicate final conversions. Do not let Gravity Forms Measurement Protocol, old thank-you/pageview logic, old Elementor submit listeners, and helper events all count the same lead.

## Gravity Forms Measurement Protocol Boundary

Gravity Forms Measurement Protocol is allowed only as an audit-only Phase 1B test unless explicitly promoted later.

For USA Form 1 tests, use an audit event such as:

- `franchise_us_inquiry_submit_server_audit`

Do not send a second GA4 `generate_lead` through Measurement Protocol while GTM/browser `generate_lead` is active.

Use lowercase GA4 parameter names. For the location test field, use:

- `location_interest`

Map it to the submitted answer value, not the literal question label.

Do not send PII or high-cardinality values to GA4, Google Ads, Meta, or dataLayer. Avoid name, email, phone, address, message text, full URLs, click IDs, GA client ID, and Gravity Forms entry ID in MP tests unless a separate approved server-side design explicitly requires them.

## GAConnector And CRM/SiteZeus Boundary

Do not overwrite GAConnector hidden fields on franchise forms.

Canada franchise forms use GAConnector hidden fields `14` through `30`; the helper path reads populated values and should not replace the GAConnector attribution layer.

Do not replace or alter Synuma, SiteZeus, CEFA Franchise API delivery, CRM routing, Gravity Forms notifications, or agency-owned business logic while doing tracking work.

## Documentation

Keep franchise status updates in the franchise docs:

- `docs/live-conversion-tracking-status-2026-05-01.md`
- `docs/franchise-canada-phase1/`
- `docs/franchise-usa-phase1/`

When a platform access limit is confirmed, document it as a reachability constraint instead of treating configured but unrelated tools as usable franchise access.
