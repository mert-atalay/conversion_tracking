# Franchise USA Phase 1 Tracking Plan

Last updated: 2026-05-01

This folder is the working implementation package for Franchise USA tracking.

Scope:
- Current/live USA franchise property: `https://franchisecefa.com` and `https://www.franchisecefa.com`
- Former USA staging property: `https://cefafranusdev.wpenginepowered.com`
- GTM account: `6004334435`
- USA franchise GTM container: `GTM-5LZMHBZL` / container `204988779`
- GA4 property: `519783092` / `CEFA Franchise - USA.`
- Linked Google Ads customers: `3820636025`, `4159217891`
- Primary website forms:
  - Gravity Forms Form `1` / Franchise Inquiry
  - Gravity Forms Form `2` / Submit a Site

## Current State

- The live USA site renders the WPCode fallback bridge from `snippets/franchise-wpcode-bridge.php`.
- Controlled submissions before GTM Version `15` proved the website-side confirmed-success dataLayer events:
  - Form `1`: `franchise_inquiry_submit`
  - Form `2`: `real_estate_site_submit`
- The helper payload uses `site_context=franchise_us`, `market=usa`, and `country=US`.
- GTM Version `15` is live as `CEFA Franchise USA Phase 1 helper-event GA4 mapping - 2026-05-01`.
- GTM Version `15` maps both helper events to USA GA4 `generate_lead` through delayed dispatch events.
- Legacy USA final conversion tags from the old Elementor/form-submit path were paused to avoid duplicate final conversions.

## Current Boundary

Active:
- USA GA4 helper-event mapping to `G-YL1KQPWV0M`.
- Non-PII helper payload fields only.
- Hostname/context filters for `franchisecefa.com` and `www.franchisecefa.com`.

Blocked:
- USA Google Ads final conversion tags until the correct USA-specific conversion labels are verified.
- USA Meta final conversion tags until the correct USA dataset/pixel is verified.
- USA GA4 custom dimensions until reporting scope and currency handling are confirmed.

Do not map USA final events to the Canada shared Meta dataset by default. USA should remain more separated unless a live campaign dependency is explicitly confirmed.

## Files

- [GTM build and QA notes](./01-gtm-build-and-qa-2026-05-01.md)
- [QA and cutover checklist](./02-qa-and-cutover-checklist.md)
