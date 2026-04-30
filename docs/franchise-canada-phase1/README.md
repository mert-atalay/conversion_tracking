# Franchise Canada Phase 1 Tracking Plan

Last updated: 2026-04-29

This folder is the working implementation package for the new Canada franchise website tracking rollout.

Scope:
- Current/live Canada franchise property: `https://franchise.cefa.ca`
- New Canada franchise staging property: `https://cefafranchise.kinsta.cloud`
- GTM account: `6004334435`
- Current Canada franchise GTM container: `GTM-TPJGHFS` / container `48104535`
- GA4 property: `259747921` / `CEFA Franchise`
- Primary website forms on staging:
  - Gravity Forms Form `1` / `Franchise Inquiry`
  - Gravity Forms Form `2` / `Site Inquiry`
  - Gravity Forms Form `3` / `Newsletter`

## Current Decision

Start Canada franchise as an audit-first Phase 1 build, not a blind copy of the old GTM container.

Use the old Canada GTM container as a reference only. The old container already contains useful IDs and micro-conversion examples, but it is built around old paths, old Elementor form selectors, and thank-you/pageview logic. The new staging site uses Gravity Forms and different page paths.

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

