# Franchise USA GTM Version 19 Attribution Field Writer

Last updated: 2026-05-06

Status: Verified

## Summary

Franchise USA had a live attribution gap: GAConnector cookies were being written on `franchisecefa.com`, but Gravity Forms hidden fields `14-30` stayed blank in the browser on the USA Form `1` and Form `2` pages.

Because WP Engine SSH was not reliable during this pass and the live source of the existing inline bridge was not found through the available WordPress MCP target, the fix was implemented in the active USA GTM container as a narrowly scoped browser-side hidden-field writer.

## GTM Change

Container:

- Account: `6004334435`
- Container: `204988779`
- Public ID: `GTM-5LZMHBZL`
- Published version: `19`
- Version name: `2026-05-06 - USA attribution hidden field writer`

Created trigger:

- ID: `269`
- Name: `CEFA - Franchise USA - DOM Ready - attribution form pages`
- Type: `domReady`
- Host scope: `^(www\.)?franchisecefa\.com$`
- Path scope: `^/available-opportunities/franchising-inquiry/?|^/partner-with-cefa/real-estate-partners/submit-a-site/?`

Created tag:

- ID: `270`
- Name: `CEFA - Franchise USA - GAConnector Hidden Field Writer`
- Type: Custom HTML
- Firing option: once per load
- Trigger: `269`

Safety boundary:

- Does not push to `dataLayer`.
- Does not call `gtag`.
- Does not call `fbq`.
- Does not send GA4, Google Ads, Meta, LinkedIn, or any other platform hit.
- Only writes hidden Gravity Forms fields `14-30` on Form `1` and Form `2`.
- Only writes blank, `undefined`, `null`, or not-set values.
- Runs only on the two live USA form pages.

## Field Mapping

The writer fills:

| Field | Meaning | Source priority |
| --- | --- | --- |
| `14` | Last click source | `gaconnector_lc_source`, then `utm_source` |
| `15` | Last click medium | `gaconnector_lc_medium`, then `utm_medium` |
| `16` | Last click campaign | `gaconnector_lc_campaign`, then `utm_campaign` |
| `17` | Last click content | `gaconnector_lc_content`, then `utm_content` |
| `18` | Last click term | `gaconnector_lc_term`, then `utm_term` |
| `19` | Last click channel | `gaconnector_lc_channel`, fallback `Unassigned` |
| `20` | Last click landing page | `gaconnector_lc_landing`, then current URL |
| `21` | Last click referrer | `gaconnector_lc_referrer`, then browser referrer |
| `22` | First click source | `gaconnector_fc_source`, then last click source / `utm_source` |
| `23` | First click medium | `gaconnector_fc_medium`, then last click medium / `utm_medium` |
| `24` | First click campaign | `gaconnector_fc_campaign`, then last click campaign / `utm_campaign` |
| `25` | First click content | `gaconnector_fc_content`, then last click content / `utm_content` |
| `26` | First click term | `gaconnector_fc_term`, then last click term / `utm_term` |
| `27` | First click channel | `gaconnector_fc_channel`, then last click channel / `Unassigned` |
| `28` | First click referrer | `gaconnector_fc_referrer`, then last click referrer / browser referrer |
| `29` | GCLID | URL `gclid`, then `_gcl_aw`, then `gaconnector_gclid` |
| `30` | GA client ID | `gaconnector_GA_Client_ID`, then parsed `_ga` |

## Test Evidence

Test A: Form `1` / Franchise Inquiry

URL:

`https://franchisecefa.com/available-opportunities/franchising-inquiry/?utm_source=qa_tracking&utm_medium=attr_wire&utm_campaign=frus_attr_wire_20260506&utm_term=frus_term&utm_content=frus_content&gclid=QA-FRUS-WIRE-20260506&fbclid=QA-FRUS-WIRE-FBCLID-20260506&msclkid=QA-FRUS-WIRE-MSCLKID-20260506`

Browser result:

- `14=qa_tracking`
- `15=attr_wire`
- `16=frus_attr_wire_20260506`
- `17=frus_content`
- `18=frus_term`
- `19=Unassigned`
- `20=https://franchisecefa.com/available-opportunities/franchising-inquiry/...`
- `21=(not set)`
- `22=qa_tracking`
- `23=attr_wire`
- `24=frus_attr_wire_20260506`
- `25=frus_content`
- `26=frus_term`
- `27=Unassigned`
- `28=(not set)`
- `29=QA-FRUS-WIRE-20260506`
- `30=2071981650.1778110823`

Test B: Form `2` / Submit a Site

URL:

`https://franchisecefa.com/partner-with-cefa/real-estate-partners/submit-a-site/?utm_source=qa_tracking&utm_medium=attr_wire&utm_campaign=frus_site_attr_wire_20260506&utm_term=frus_site_term&utm_content=frus_site_content&gclid=QA-FRUS-SITE-WIRE-20260506&fbclid=QA-FRUS-SITE-WIRE-FBCLID-20260506&msclkid=QA-FRUS-SITE-WIRE-MSCLKID-20260506`

Browser result:

- `14=qa_tracking`
- `15=attr_wire`
- `16=frus_site_attr_wire_20260506`
- `17=frus_site_content`
- `18=frus_site_term`
- `19=Unassigned`
- `20=https://franchisecefa.com/partner-with-cefa/real-estate-partners/submit-a-site/...`
- `21=(not set)`
- `22=qa_tracking`
- `23=attr_wire`
- `24=frus_site_attr_wire_20260506`
- `25=frus_site_content`
- `26=frus_site_term`
- `27=Unassigned`
- `28=(not set)`
- `29=QA-FRUS-SITE-WIRE-20260506`
- `30=779296744.1778110844`

## Remaining QA

- Submit one controlled Form `1` lead and confirm the saved Gravity Forms entry retains fields `14-30`.
- Submit one controlled Form `2` lead and confirm the saved Gravity Forms entry retains fields `14-30`.
- Confirm helper event payloads continue to carry the same clean attribution values after confirmed success.
- Keep Gravity Forms Measurement Protocol audit-only if tested later; do not use it as a duplicate primary `generate_lead` source.
