# Live Main Conversion Event Audit

Date: 2026-05-04

Scope:

- Parent: `https://cefa.ca`
- Franchise Canada: `https://franchise.cefa.ca`
- Franchise USA: `https://franchisecefa.com` and `https://www.franchisecefa.com`

Initial audit note: no backend settings, GTM publishing, GA4 settings, Google Ads settings, or Meta settings were changed during the first audit pass. Later on 2026-05-04, targeted live fixes were deployed: parent `cefa-conversion-tracking` was updated to `0.4.3`, the franchise WPCode bridge was patched to backfill/clean existing GAConnector hidden attribution fields before Gravity Forms saves the entry, Franchise USA GTM Version `16` moved Meta to the new USA dataset `1531247935333023`, Franchise USA GTM Version `17` paused old active micro/click tags, Franchise USA GTM Version `18` added a Meta Lead reliability fallback, and Meta custom conversion `1915200622465036` / `USA Franchise Lead` was created.

## Executive Status

| Site | Main conversion event | Live status | Evidence level | Remaining issue |
|---|---|---|---|---|
| Parent `cefa.ca` | `school_inquiry_submit` -> GA4 `generate_lead` | Working | GA4 processed report, public runtime, GTM JS, WP plugin/feed check | Plugin deployment gap resolved: live now runs `cefa-conversion-tracking` `0.4.3`. Mobile/post-change Ads request QA still pending. |
| Franchise Canada Form 1 | `franchise_inquiry_submit` -> GA4 `generate_lead` | Working | Live submission, dataLayer, network, GA4 realtime, Gravity Forms entry | None blocking main conversion. Attribution/gclid behavior needs cleanup review. |
| Franchise Canada Form 2 | `real_estate_site_submit` -> GA4 `generate_lead` | Working | Live submission, dataLayer, network, GA4 realtime, Gravity Forms entry | GAConnector stale-`gclid` cleanup patched and verified with entry `46`. |
| Franchise USA Form 1 | `franchise_inquiry_submit` -> GA4 `generate_lead`; Meta `Lead` via USA dataset `1531247935333023` | Working for GA4/helper path; Meta browser runtime configured; USA inquiry custom conversion created | Live submission, dataLayer, network, GA4 realtime, Gravity Forms entry, GTM Version `18`, fresh public runtime check, Meta custom conversion API response | Attribution cleanup patched and verified with entry `37`; active Gravity Forms Google Analytics feed remains for Form 1; Meta Events Manager live receipt confirmation pending. |
| Franchise USA Form 2 | `real_estate_site_submit` -> GA4 `generate_lead`; Meta `Lead` via USA dataset `1531247935333023` | Working for GA4/helper path; Meta browser runtime configured | Live submission, dataLayer, network, GA4 realtime, Gravity Forms entry, GTM Version `18`, fresh public runtime check | Attribution cleanup patched and verified with entry `36`; Meta Events Manager live receipt confirmation pending. |

Bottom line: the main browser-side conversion event path is working on all live sites/forms checked. The parent plugin safeguard deployment, franchise GAConnector cleanup, USA Meta dataset split, USA GTM legacy micro/click cleanup, USA Meta Lead fallback, and USA inquiry custom conversion creation are now complete. Remaining work is USA Gravity Forms add-on duplicate-source cleanup, parent mobile/post-change request QA, Meta Events Manager live receipt confirmation, and delayed processed GA4/BQ reporting confirmation.

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
| `GTM-5LZMHBZL` | Franchise USA | `AW-11088792613`, `G-YL1KQPWV0M`, Meta pixel `1531247935333023`, `franchise_inquiry_submit`, `real_estate_site_submit`, `cefa_franchise_us_inquiry_dispatch`, `cefa_franchise_us_site_dispatch`, `generate_lead`. Public runtime check after Version `17` found zero active occurrences of `918227085392601` and zero old click markers/labels; Version `18` added Meta `Lead` reliability fallback. |

## WordPress / Gravity Forms Source Audit

| Site | Tracking plugin state | Gravity Forms feed state |
|---|---|---|
| Parent `cefa.ca` | `cefa-conversion-tracking` active `0.4.3`; `cefa-school-manager` active `1.0.18`; Gravity Forms active `2.10.1`. | No Gravity Forms Google Analytics feed found. Only active feed found was Mailchimp Form 1. |
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

Post-patch verification:

- The franchise WPCode bridge now backfills existing hidden attribution fields `14` through `30` before Gravity Forms saves the entry.
- For `gclid`, the bridge prefers the current Google `_gcl_aw` value over a stale `gaconnector_gclid` or stale hidden field `29`.
- A controlled Form 2 retest intentionally left hidden field `29` stale before submit. The resulting dataLayer payload and Gravity Forms entry `46` saved `gclid=QA-FRCA-PATCH-SITE-20260504`, matching the current landing URL / `_gcl_aw` value.
- Entry `46` also saved clean separate values for `14=qa_tracking`, `15=live_patch`, `16=gaconnector_backfill_20260504`, `29=QA-FRCA-PATCH-SITE-20260504`, and `30=1065795917.1777927212`.

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
- This attribution gap was open during the initial audit and was resolved by the post-patch retest below.

Post-patch verification:

- A controlled Form 1 retest started with blank GAConnector hidden fields and intentionally stale hidden field `29`.
- The resulting `franchise_inquiry_submit` payload carried clean attribution values: `lc_source=qa_tracking`, `lc_medium=live_patch`, `lc_campaign=gaconnector_backfill_20260504`, `gclid=QA-FRUS-PATCH-INQ-20260504`, and `ga_client_id=1930300797.1777927657`.
- Gravity Forms entry `37` saved the same attribution fields plus matching `cefa_conversion_tracking_event_id=b8ac84bf-c7a2-458e-8af6-68a06fb75e97`.

Duplicate-source caveat:

- The USA Gravity Forms Google Analytics add-on remains active with a Form 1 feed.
- The helper/GTM event worked, but the active add-on feed may create duplicate or alternate GA4 events later.

Meta update after this submission:

- USA GTM Version `16` mapped the existing Form 1 dispatch event to Meta standard `Lead` on dataset `1531247935333023`; Versions `17` and `18` retained that final helper path.
- The old shared Meta pixel block was removed from USA WordPress Insert Headers and Footers.

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
- This confirmed the pre-patch USA helper payload was not yet reading/passing attribution the same way Canada did; the post-patch retest below resolved the gap for Form 2.

Post-patch verification:

- A controlled Form 2 retest started with blank GAConnector hidden fields and intentionally stale hidden field `29`.
- The resulting `real_estate_site_submit` payload carried clean attribution values: `lc_source=qa_tracking`, `lc_medium=live_patch`, `lc_campaign=gaconnector_backfill_20260504`, `gclid=QA-FRUS-PATCH-SITE-20260504`, and `ga_client_id=1618510533.1777927481`.
- Gravity Forms entry `36` saved the same attribution fields plus matching `cefa_conversion_tracking_event_id=e91e2fb5-8a9c-4369-b1d7-736b9c4a165e`.

Meta update after this submission:

- USA GTM Version `16` mapped the existing Form 2 dispatch event to Meta standard `Lead` on dataset `1531247935333023`; Versions `17` and `18` retained that final helper path.
- Fresh headless Chrome verification after WP Engine cache purge saw Meta config for `1531247935333023` and zero old shared-dataset Meta requests.

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

1. Parent: run one controlled mobile Form 4 test and confirm the post-change Ads request uses `AW-802334988/cFt-CMrLufgCEIzSyv4C`.
2. Franchise USA: disable or convert the active Gravity Forms Google Analytics Form 1 feed to audit-only so it cannot compete with the helper/GTM final conversion path.
3. GA4: re-run processed Data API reports after the franchise submissions have had time to process.
4. BigQuery: enable or verify GA4 export datasets for Franchise Canada and Franchise USA if dashboard/reporting parity is required.
5. Meta: confirm Events Manager live receipt because this audit now confirms browser/GTM-side markers and USA custom conversion creation, but not the Meta UI receipt of a fresh live `Lead`.

## Signoff

| Surface | Parent | Franchise Canada | Franchise USA |
|---|---|---|---|
| Live URL/form renders | Pass | Pass | Pass |
| Correct GTM container present | Pass | Pass | Pass, Version `18` |
| Website-side primary event present | Pass | Pass | Pass |
| GA4 primary event sent/received | Pass processed | Pass realtime | Pass realtime |
| Gravity Forms entry saves event ID | Previously verified; not re-submitted in this audit | Pass | Pass |
| CRM/Synuma delivery marker | Not re-tested in this audit | Pass | Pass |
| Attribution fields complete | Mostly pass from previous parent work | Pass for patched Form 2 retest | Pass for patched Form 1 and Form 2 retests |
| Duplicate source risk | Low; no GF GA feed found | Low; no GF add-on feed found | Medium; GF GA Form 1 feed still active |
| Meta dataset boundary | Parent shared/current dataset | Canada shared dataset retained for transition | USA dataset `1531247935333023` active through GTM; `USA Franchise Lead` custom conversion exists; Events Manager live receipt signoff pending |
