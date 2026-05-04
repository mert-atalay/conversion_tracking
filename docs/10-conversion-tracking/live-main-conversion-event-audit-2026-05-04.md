# Live Main Conversion Event Audit

Date: 2026-05-04

Scope:

- Parent: `https://cefa.ca`
- Franchise Canada: `https://franchise.cefa.ca`
- Franchise USA: `https://franchisecefa.com` and `https://www.franchisecefa.com`

No backend settings, GTM publishing, GA4 settings, Google Ads settings, or Meta settings were changed during this audit. Controlled live form submissions were made for Franchise Canada and Franchise USA to verify the primary conversion events after launch.

## Executive Status

| Site | Main conversion event | Live status | Evidence level | Remaining issue |
|---|---|---|---|---|
| Parent `cefa.ca` | `school_inquiry_submit` -> GA4 `generate_lead` | Working | GA4 processed report, public runtime, GTM JS, WP plugin/feed check | Live parent plugin is still `0.4.1`; repo has later safeguard package `0.4.3` not deployed. |
| Franchise Canada Form 1 | `franchise_inquiry_submit` -> GA4 `generate_lead` | Working | Live submission, dataLayer, network, GA4 realtime, Gravity Forms entry | None blocking main conversion. Attribution/gclid behavior needs cleanup review. |
| Franchise Canada Form 2 | `real_estate_site_submit` -> GA4 `generate_lead` | Working | Live submission, dataLayer, network, GA4 realtime, Gravity Forms entry | Same-session GAConnector `gclid` used the earlier inquiry-test click ID. |
| Franchise USA Form 1 | `franchise_inquiry_submit` -> GA4 `generate_lead` | Working | Live submission, dataLayer, network, GA4 realtime, Gravity Forms entry | Helper payload is missing attribution values; active Gravity Forms Google Analytics feed remains for Form 1. |
| Franchise USA Form 2 | `real_estate_site_submit` -> GA4 `generate_lead` | Working | Live submission, dataLayer, network, GA4 realtime, Gravity Forms entry | Helper payload is missing attribution values. |

Bottom line: the main browser-side conversion event path is working on all live sites/forms checked. The remaining work is not "main event missing"; it is attribution completeness, USA duplicate-source cleanup, parent plugin safeguard deployment, and delayed processed GA4/BQ reporting confirmation.

## Live URL Runtime Audit

| URL | Status | Expected container | Form/bridge evidence |
|---|---:|---|---|
| `https://cefa.ca/submit-an-inquiry-today/?location=abbotsford-highstreet` | 200 | `GTM-NZ6N7WNC` | `gform_4`, `cefa-conversion-tracking`, `school_inquiry_submit` markers present. |
| `https://franchise.cefa.ca/available-opportunities/franchising-inquiry/` | 200 | `GTM-TPJGHFS` | `gform_1`, franchise bridge markers present. |
| `https://franchise.cefa.ca/partner-with-cefa/real-estate-partners/submit-a-site/` | 200 | `GTM-TPJGHFS` | `gform_2`, franchise bridge markers present. |
| `https://franchisecefa.com/available-opportunities/franchising-inquiry/` | 200 | `GTM-5LZMHBZL` | `gform_1`, franchise bridge markers present. |
| `https://franchisecefa.com/partner-with-cefa/real-estate-partners/submit-a-site/` | 200 | `GTM-5LZMHBZL` | `gform_2`, franchise bridge markers present. |
| `https://www.franchisecefa.com/` | 200 final URL `https://franchisecefa.com/` | `GTM-5LZMHBZL` | `www` redirects/canonicalizes to the non-www USA site. |

## GTM Public Container Audit

Public `gtm.js` marker checks:

| Container | Site | Required markers found |
|---|---|---|
| `GTM-NZ6N7WNC` | Parent | `AW-802334988`, `G-T65G018LYB`, Meta pixel `918227085392601`, `school_inquiry_submit`, `generate_lead`. |
| `GTM-TPJGHFS` | Franchise Canada | `AW-802334988`, `AW-11088792613`, `G-6EMKPZD7RD`, Meta pixel `918227085392601`, `franchise_inquiry_submit`, `real_estate_site_submit`, `generate_lead`. |
| `GTM-5LZMHBZL` | Franchise USA | `AW-11088792613`, `G-YL1KQPWV0M`, Meta pixel `918227085392601`, `franchise_inquiry_submit`, `real_estate_site_submit`, `cefa_franchise_us_inquiry_dispatch`, `cefa_franchise_us_site_dispatch`, `generate_lead`. |

## WordPress / Gravity Forms Source Audit

| Site | Tracking plugin state | Gravity Forms feed state |
|---|---|---|
| Parent `cefa.ca` | `cefa-conversion-tracking` active `0.4.1`; `cefa-school-manager` active `1.0.18`; Gravity Forms active `2.10.1`. | No Gravity Forms Google Analytics feed found. Only active feed found was Mailchimp Form 1. |
| Franchise Canada | `cefa-franchise-mcp-control` active `0.1.12`; Gravity Forms active `2.10.1`. | No active Gravity Forms add-on feed rows found. |
| Franchise USA | `cefa-franchise-mcp-control` active `0.1.13`; Gravity Forms active `2.10.1`; Gravity Forms Google Analytics active `2.4.1`. | Active `gravityformsgoogleanalytics` feed exists for Form 1. This is a duplicate-source risk until disabled or proven audit-only. |

## GA4 Evidence

### Parent GA4 Processed Report

Property: `267558140` / Main Site GA4

Date: `2026-05-04`

| Event | Host | Tracking source | Form ID | Event count | Key events |
|---|---|---|---|---:|---:|
| `generate_lead` | `cefa.ca` | `helper_plugin` | `4` | 18 | 18 |

Interpretation:

- Parent main conversion is processing as GA4 `generate_lead`.
- This confirms live parent traffic is already reaching the main GA4 key event path.
- A new live parent test submission was not created in this audit to avoid an unnecessary parent/KinderTales lead.

### Franchise Canada Realtime Report

Property: `259747921` / CEFA Franchise

Realtime after controlled Form 1 and Form 2 submissions:

| Event | Event count |
|---|---:|
| `generate_lead` | 2 |

Interpretation:

- Canada Form 1 and Form 2 both reached GA4 realtime after submission.
- Same-day processed Data API rows may lag; do not treat the empty same-day processed report as a failure immediately after testing.

### Franchise USA Realtime Report

Property: `519783092` / CEFA Franchise - USA

Realtime after controlled Form 1 and Form 2 submissions:

| Event | Event count |
|---|---:|
| `generate_lead` | 2 |

Interpretation:

- USA Form 1 and Form 2 both reached GA4 realtime after submission.
- Same-day processed Data API rows may lag; do not treat the empty same-day processed report as a failure immediately after testing.

## Controlled Submission Evidence

### Franchise Canada Form 1 - Franchise Inquiry

Source URL:

`https://franchise.cefa.ca/available-opportunities/franchising-inquiry/?utm_source=qa_tracking&utm_medium=live_audit&utm_campaign=conversion_event_recheck_20260504&gclid=QA-FRCA-MAIN-20260504`

Result:

- Successful thank-you URL: `/inquiry-thank-you/?location=edmonton-ab&inquiry=true&cefa_tracking=1&cefa_tracking_event_id=bbf3bbef-2154-48d9-b036-8f54e4bee3e3`
- DataLayer event: `franchise_inquiry_submit`
- Event ID: `bbf3bbef-2154-48d9-b036-8f54e4bee3e3`
- Payload context: `site_context=franchise_ca`, `market=canada`, `country=CA`, `form_id=1`, `form_family=franchise_inquiry`, `tracking_source=helper_plugin`
- Network evidence: GA4 `generate_lead` to `G-6EMKPZD7RD`; Google Ads conversion request; LinkedIn attribution trigger.
- Gravity Forms entry: Form 1 entry `44`; `cefa_conversion_tracking_event_id` matched the dataLayer event ID; `cefa_synuma_lead_id` was present.

Status: pass.

### Franchise Canada Form 2 - Real Estate Site Submit

Source URL:

`https://franchise.cefa.ca/partner-with-cefa/real-estate-partners/submit-a-site/?utm_source=qa_tracking&utm_medium=live_audit&utm_campaign=conversion_event_recheck_20260504&gclid=QA-FRCA-SITE-20260504`

Result:

- Successful thank-you URL: `/site-thank-you/?cefa_tracking=1&cefa_tracking_event_id=740e7413-9cbc-4410-a19f-53a5e0e34e80`
- DataLayer event: `real_estate_site_submit`
- Dispatch event: `cefa_real_estate_site_dispatch`
- Event ID: `740e7413-9cbc-4410-a19f-53a5e0e34e80`
- Payload context: `site_context=franchise_ca`, `market=canada`, `country=CA`, `form_id=2`, `form_family=site_inquiry`, `tracking_source=helper_plugin`
- Network evidence: GA4 `generate_lead` to `G-6EMKPZD7RD` with `value=250`, `currency_code=CAD`; Google Ads conversion requests; LinkedIn conversion trigger.
- Gravity Forms entry: Form 2 entry `45`; `cefa_conversion_tracking_event_id` matched the dataLayer event ID; `cefa_synuma_lead_id` was present.

Status: pass for the main conversion event.

Attribution caveat:

- The helper payload and Gravity Forms field `29` carried `QA-FRCA-MAIN-20260504` as `gclid` while the Form 2 landing URL had `QA-FRCA-SITE-20260504`.
- Browser cookies showed `_gcl_aw` had the current site-submit `gclid`, but `gaconnector_gclid` still held the earlier inquiry-test `gclid`.
- This is an attribution cleanup item, not a main conversion-event failure.

### Franchise USA Form 1 - Franchise Inquiry

Source URL:

`https://franchisecefa.com/available-opportunities/franchising-inquiry/?utm_source=qa_tracking&utm_medium=live_audit&utm_campaign=conversion_event_recheck_20260504&gclid=QA-FRUS-MAIN-20260504`

Result:

- Successful thank-you URL: `/inquiry-thank-you/?location=atlanta&inquiry=true&cefa_tracking=1&cefa_tracking_event_id=cd1297db-30a6-46ab-b22a-169f01230878`
- DataLayer event: `franchise_inquiry_submit`
- Dispatch event: `cefa_franchise_us_inquiry_dispatch`
- Event ID: `cd1297db-30a6-46ab-b22a-169f01230878`
- Payload context: `site_context=franchise_us`, `market=usa`, `country=US`, `form_id=1`, `form_family=franchise_inquiry`, `tracking_source=helper_plugin`
- Network evidence: GA4 `generate_lead` to `G-YL1KQPWV0M` with `value=650`, `currency_code=USD`.
- Gravity Forms entry: Form 1 entry `34`; `cefa_conversion_tracking_event_id` matched the dataLayer event ID; `cefa_synuma_lead_id` was present.

Status: pass for the main conversion event.

Attribution caveat:

- Helper payload attribution values were blank: `lc_source`, `lc_medium`, `lc_campaign`, `gclid`, and `ga_client_id`.
- Gravity Forms entry did not return the same attribution field keys checked on Canada (`14`, `15`, `16`, `29`, `30`).
- USA attribution capture still needs cleanup before attribution signoff.

Duplicate-source caveat:

- The USA Gravity Forms Google Analytics add-on remains active with a Form 1 feed.
- The helper/GTM event worked, but the active add-on feed may create duplicate or alternate GA4 events later.

### Franchise USA Form 2 - Real Estate Site Submit

Source URL:

`https://franchisecefa.com/partner-with-cefa/real-estate-partners/submit-a-site/?utm_source=qa_tracking&utm_medium=live_audit&utm_campaign=conversion_event_recheck_20260504&gclid=QA-FRUS-SITE-20260504`

Result:

- Successful thank-you URL: `/site-thank-you/?cefa_tracking=1&cefa_tracking_event_id=c6492cf5-655e-4af0-abef-c6af792eff66`
- DataLayer event: `real_estate_site_submit`
- Dispatch event: `cefa_franchise_us_site_dispatch`
- Event ID: `c6492cf5-655e-4af0-abef-c6af792eff66`
- Payload context: `site_context=franchise_us`, `market=usa`, `country=US`, `form_id=2`, `form_family=site_inquiry`, `tracking_source=helper_plugin`
- Network evidence: GA4 `generate_lead` to `G-YL1KQPWV0M` with `value=250`, `currency_code=USD`.
- Gravity Forms entry: Form 2 entry `35`; `cefa_conversion_tracking_event_id` matched the dataLayer event ID; `cefa_synuma_lead_id` was present.

Status: pass for the main conversion event.

Attribution caveat:

- A clean isolated browser context had GAConnector cookies populated with `QA-FRUS-SITE-20260504`, but the helper dataLayer payload still showed blank attribution values.
- This confirms the USA helper payload is not yet reading/passing attribution the same way Canada does.

## BigQuery / Reporting Export State

BigQuery datasets checked in project `marketing-api-488017`:

| GA4 property | Dataset | Status |
|---|---|---|
| Parent `267558140` | `analytics_267558140` | Exists. Parent helper events are exporting. |
| Franchise Canada `259747921` | `analytics_259747921` | Not present at audit time. |
| Franchise USA `519783092` | `analytics_519783092` | Not present at audit time. |

Interpretation:

- Parent can be validated through GA4 processed reports and BigQuery export.
- Franchise Canada and USA currently need GA4 realtime/processed reports until their exports are configured or become available.

## Remaining Action Plan

1. Parent: deploy `cefa-conversion-tracking` `0.4.3` or newer when approved, then run one controlled Form 4 test to confirm the `event_id` safeguard.
2. Franchise Canada: keep the helper/GTM primary conversion path as live; review GAConnector `gclid` overwrite/last-click behavior before attribution signoff.
3. Franchise USA: fix attribution payload capture so helper events and Gravity Forms entries include the required UTM/click/GA client fields.
4. Franchise USA: disable or convert the active Gravity Forms Google Analytics Form 1 feed to audit-only so it cannot compete with the helper/GTM final conversion path.
5. GA4: re-run processed Data API reports after the franchise submissions have had time to process.
6. BigQuery: enable or verify GA4 export datasets for Franchise Canada and Franchise USA if dashboard/reporting parity is required.
7. Meta: separately confirm Events Manager receipt/custom conversions because this audit confirmed browser/GTM-side markers but not Meta UI/API reporting.

## Signoff

| Surface | Parent | Franchise Canada | Franchise USA |
|---|---|---|---|
| Live URL/form renders | Pass | Pass | Pass |
| Correct GTM container present | Pass | Pass | Pass |
| Website-side primary event present | Pass | Pass | Pass |
| GA4 primary event sent/received | Pass processed | Pass realtime | Pass realtime |
| Gravity Forms entry saves event ID | Previously verified; not re-submitted in this audit | Pass | Pass |
| CRM/Synuma delivery marker | Not re-tested in this audit | Pass | Pass |
| Attribution fields complete | Mostly pass from previous parent work | Partial: `gclid` behavior needs cleanup | Fail/partial: payload fields blank |
| Duplicate source risk | Low; no GF GA feed found | Low; no GF add-on feed found | Medium; GF GA Form 1 feed still active |
