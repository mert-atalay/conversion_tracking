# Franchise CA/USA Tracking Status

Last updated: 2026-05-03 17:38 PDT

## Scope

| Field | Value |
|---|---|
| Workstream | Conversion tracking |
| Properties | `franchise.cefa.ca`, `franchisecefa.com`, `www.franchisecefa.com` |
| Systems checked | Live form URLs, GTM runtime scripts, GA4 Data API, GA4 Admin links, Supermetrics Google Ads reporting |
| Live writes made | No |
| Platform settings changed | No |

This status covers franchise tracking readiness only. Paid-media optimization decisions belong in `docs/50-paid-media/`, and naming/UTM rules belong in `docs/40-naming-convention/`.

## Current Done / Left Summary

| Area | Status | What is done | What is left |
|---|---|---|---|
| Franchise Canada website source | Verified | Both current form URLs return `200`, load `GTM-TPJGHFS`, and render the WPCode bridge markers. | Continue monitoring. No website-source change needed for ads launch. |
| Franchise Canada GTM runtime | Verified | `GTM-TPJGHFS` still contains `franchise_inquiry_submit`, `real_estate_site_submit`, `cefa_franchise_inquiry_dispatch`, and `cefa_real_estate_site_dispatch`. | No runtime action identified from this check. |
| Franchise Canada GA4 reporting | Partial | GA4 property `259747921` reports `4` processed `generate_lead` rows on `franchise.cefa.ca` for `2026-05-01` through `2026-05-04`; `1` row has helper metadata and `3` rows are `(not set)`. | Confirm Form 2 helper metadata in processed reports after another controlled Form 2 test or real lead. |
| Franchise Canada Google Ads | Partial | Google Ads reporting for account `3820636025` is readable; current evidence still shows `fr_application_submit` primary while `generate_lead (GA4)`, `fr_site_form_submit`, and `fr_inquiry_submit` are secondary. | Media owner must decide which franchise Canada action is primary for bidding. Do not change primary status from repo evidence alone. |
| Franchise Canada Meta | Partial | Browser/network evidence from prior controlled tests showed Canada events received on pixel/dataset `918227085392601`. | Direct Events Manager custom-conversion confirmation is still pending. |
| Franchise USA website source | Verified | Both current form URLs return `200`, load `GTM-5LZMHBZL`, and render WPCode bridge markers. | Continue monitoring. No website-source change needed before the GA4 final-event issue is isolated. |
| Franchise USA GTM runtime | Verified | `GTM-5LZMHBZL` still contains `franchise_inquiry_submit`, `real_estate_site_submit`, `cefa_franchise_us_inquiry_dispatch`, `cefa_franchise_us_site_dispatch`, and `G-YL1KQPWV0M`. | No runtime action identified from the public `gtm.js` check. |
| Franchise USA GA4 base collection | Verified | GA4 property `519783092` reports `page_view`, `session_start`, `first_visit`, `user_engagement`, `scroll`, `form_start`, `form_submit`, and `click` for host `franchisecefa.com` over `2026-05-01` through `2026-05-04`. | None for base traffic collection. |
| Franchise USA GA4 final lead collection | Partial | Form 2 had browser-resource evidence of a `generate_lead` hit to `G-YL1KQPWV0M` with helper metadata on 2026-05-03. | GA4 Data API still reports `0` processed `generate_lead` rows for USA over `2026-05-01` through `2026-05-04`. Form 1 GA4 final-hit evidence is still missing. |
| Franchise USA GA4 property settings | Verified | GA4 property `519783092` exists, timezone is `America/Los_Angeles`, and default currency is currently `CAD`. It is linked to Google Ads customers `3820636025` and `4159217891`. | Open question: confirm whether USA property currency should remain `CAD` or be changed to `USD` before reporting signoff. |
| Franchise USA Google Ads | Partial | Google Ads reporting confirms USA-related imported conversion actions exist in both linked accounts. The checked USA final actions still have `0` all conversions. | Decide which account and conversion action should be the USA bidding/primary action before activating final Google Ads helper-event tags. |
| Franchise USA Meta | Pending | USA final Meta helper-event tags remain intentionally blocked. | Confirm the USA Meta pixel/dataset. Do not assume Canada shared dataset strategy applies to USA. |
| Gravity Forms Measurement Protocol | Pending | MP remains allowed only as an audit-only layer. | If tested, send `franchise_us_inquiry_submit_server_audit`; do not send a second `generate_lead`. Use lowercase `location_interest` and no PII/high-cardinality values. |

## Fresh Evidence From 2026-05-03

### Live Form URLs

| Property | Form | URL | Status |
|---|---|---|---|
| Canada | Form `1` / Franchise Inquiry | `https://franchise.cefa.ca/available-opportunities/franchising-inquiry/` | Verified: `200`, `GTM-TPJGHFS`, bridge markers present |
| Canada | Form `2` / Submit a Site | `https://franchise.cefa.ca/partner-with-cefa/real-estate-partners/submit-a-site/` | Verified: `200`, `GTM-TPJGHFS`, bridge markers present |
| USA | Form `1` / Franchise Inquiry | `https://franchisecefa.com/available-opportunities/franchising-inquiry/` | Verified: `200`, `GTM-5LZMHBZL`, bridge markers present |
| USA | Form `2` / Submit a Site | `https://franchisecefa.com/partner-with-cefa/real-estate-partners/submit-a-site/` | Verified: `200`, `GTM-5LZMHBZL`, bridge markers present |

### GA4 Processed Reports

Canada property `259747921`, date range `2026-05-01` through `2026-05-04`, filter `eventName=generate_lead`:

| Host | `site_context` | `form_family` | `lead_type` | `tracking_source` | Event count | Status |
|---|---|---|---|---|---:|---|
| `franchise.cefa.ca` | `(not set)` | `(not set)` | `(not set)` | `(not set)` | `3` | Partial |
| `franchise.cefa.ca` | `franchise_ca` | `franchise_inquiry` | `franchise_lead` | `helper_plugin` | `1` | Verified |

USA property `519783092`, date range `2026-05-01` through `2026-05-04`, filter `eventName=generate_lead`:

| Result | Status |
|---|---|
| No processed rows returned | Pending |

USA property `519783092`, same date range, host filter `franchisecefa.com`:

| Event | Event count | Status |
|---|---:|---|
| `page_view` | `28` | Verified |
| `session_start` | `25` | Verified |
| `first_visit` | `18` | Verified |
| `user_engagement` | `12` | Verified |
| `scroll` | `5` | Verified |
| `form_start` | `2` | Verified |
| `click` | `1` | Verified |
| `form_submit` | `1` | Verified |

Interpretation: USA GA4 base collection is working, but USA final lead processing is not yet verified in GA4 reports.

### Google Ads Reporting

Supermetrics Google Ads reporting is authenticated for `mert.atalay@cefa.ca` and can read:

- `3820636025` / `CEFA Franchisor`
- `4159217891` / `CEFA $3000`

Canada/franchise-relevant actions in `3820636025` for `2025-05-01` through `2026-05-04`:

| Conversion action | Tracker ID | Primary for goal | All conversions | Status |
|---|---|---:|---:|---|
| `fr_application_submit` | `6472168961` | `true` | `96` | Verified |
| `generate_lead (GA4)` | `6480960234` | `false` | `82.51` | Verified |
| `fr_site_form_submit` | `6472168970` | `false` | `3` | Verified |
| `fr_inquiry_submit` | `6472168964` | `false` | `0` | Verified |

USA-related actions in `3820636025`:

| Conversion action | Tracker ID | Primary for goal | All conversions | Status |
|---|---|---:|---:|---|
| `Application Submit (USA)` | `7482298930` | `true` | `0` | Partial |
| `CEFA Franchise - USA. (web) generate_lead` | `7499744287` | `false` | `0` | Partial |
| `CEFA Franchise - USA. (web) ads_conversion_submit_lead_form` | `7482257746` | `false` | `0` | Partial |

USA-related actions in `4159217891`:

| Conversion action | Tracker ID | Primary for goal | All conversions | Status |
|---|---|---:|---:|---|
| `CEFA Franchise - USA. (web) generate_lead` | `7499970414` | `false` | `0` | Partial |
| `Cefafranchise.com | Request Info Submission` | `293368274` | `false` | `0` | Partial |

Interpretation: USA conversion actions exist, but the final action and account choice are not ready for bidding until the media owner confirms the intended setup and at least one current test conversion is observed.

## Immediate Next Tasks

| Priority | Task | Status | Why |
|---:|---|---|---|
| 1 | Run a fresh controlled USA Form 1 and Form 2 QA with browser network capture, GTM Preview or equivalent, and GA4 DebugView if available. | Pending | USA GA4 base collection works, but processed `generate_lead` is still missing. |
| 2 | Inspect USA GTM Version `15` GA4 final tags if GTM admin/tool access is available. | Pending | Public `gtm.js` proves markers exist, not why GA4 final rows are not processing. |
| 3 | Confirm USA Google Ads bidding account and primary conversion action. | Open question | Both linked accounts contain USA-related actions; current checked actions have zero all conversions. |
| 4 | Confirm USA Meta dataset/pixel and whether a separate USA dataset should be used. | Open question | USA should remain separated unless a live campaign dependency says otherwise. |
| 5 | Confirm whether USA GA4 default currency should remain `CAD` or become `USD`. | Open question | Current property default is `CAD`; the Form 2 browser hit used `USD`. |
| 6 | Confirm Canada Meta custom conversions in Events Manager. | Pending | Browser receipt is verified, but Events Manager custom-conversion setup is not. |
| 7 | Make Canada Google Ads primary/secondary decision with the media owner. | Open question | Current primary action may not match the new helper-event path. |

## Guardrails

- Do not create duplicate final conversions.
- Do not activate Gravity Forms Measurement Protocol as a second `generate_lead` source.
- Do not send PII or high-cardinality values to GA4, Google Ads, Meta, or dataLayer.
- Do not overwrite GAConnector hidden fields.
- Do not replace Synuma, SiteZeus, CRM delivery, Gravity Forms UI, or agency-owned business logic.
- Keep website events neutral and let GTM map them to platform events.
