# Franchise CA/USA Tracking Status

Last updated: 2026-05-04

## Scope

| Field | Value |
|---|---|
| Workstream | Conversion tracking |
| Properties | `franchise.cefa.ca`, `franchisecefa.com`, `www.franchisecefa.com` |
| Systems checked | Live form URLs, GTM runtime scripts, GA4 Data API, GA4 Admin links, Supermetrics Google Ads reporting, WP Engine/WP-CLI, controlled live form submissions, USA Meta pixel runtime |
| Live writes made | Yes: franchise WPCode bridge attribution cleanup patch deployed to Canada and USA on 2026-05-04; USA old inline Meta pixel removed from Insert Headers and Footers. |
| Platform settings changed | Yes: USA GTM Version `16` was published to move Meta to USA dataset `1531247935333023`. No GA4 or Google Ads settings changed. |

This status covers franchise tracking readiness only. Paid-media optimization decisions belong in `docs/50-paid-media/`, and naming/UTM rules belong in `docs/40-naming-convention/`.

## Current Done / Left Summary

| Area | Status | What is done | What is left |
|---|---|---|---|
| Franchise Canada website source | Verified | Both current form URLs return `200`, load `GTM-TPJGHFS`, and render the WPCode bridge markers. The WPCode bridge now backfills missing attribution fields and fixes stale `gclid` from current `_gcl_aw`. | Continue monitoring. No website-source change needed for ads launch. |
| Franchise Canada GTM runtime | Verified | `GTM-TPJGHFS` still contains `franchise_inquiry_submit`, `real_estate_site_submit`, `cefa_franchise_inquiry_dispatch`, and `cefa_real_estate_site_dispatch`. | No runtime action identified from this check. |
| Franchise Canada GA4 reporting | Partial | GA4 property `259747921` reports processed `generate_lead` rows from earlier checks, and realtime passed for controlled Form 1/Form 2 tests. Form 2 post-patch dataLayer and Gravity Forms entry now have clean attribution. | Confirm Form 2 helper metadata in processed reports after processing delay. |
| Franchise Canada Google Ads | Partial | Google Ads reporting for account `3820636025` is readable; current evidence still shows `fr_application_submit` primary while `generate_lead (GA4)`, `fr_site_form_submit`, and `fr_inquiry_submit` are secondary. | Media owner must decide which franchise Canada action is primary for bidding. Do not change primary status from repo evidence alone. |
| Franchise Canada Meta | Partial | Browser/network evidence from prior controlled tests showed Canada events received on pixel/dataset `918227085392601`. | Direct Events Manager custom-conversion confirmation is still pending. |
| Franchise USA website source | Verified | Both current form URLs return `200`, load `GTM-5LZMHBZL`, and render WPCode bridge markers. The WPCode bridge now backfills missing GAConnector fields from cookies before Gravity Forms saves Form 1/Form 2 entries. | Continue monitoring. Duplicate-source cleanup remains separate. |
| Franchise USA GTM runtime | Verified | `GTM-5LZMHBZL` Version `16` contains `franchise_inquiry_submit`, `real_estate_site_submit`, `cefa_franchise_us_inquiry_dispatch`, `cefa_franchise_us_site_dispatch`, `G-YL1KQPWV0M`, and Meta dataset `1531247935333023`. | Confirm Meta Events Manager receipt/custom conversions. |
| Franchise USA GA4 base collection | Verified | GA4 property `519783092` reports `page_view`, `session_start`, `first_visit`, `user_engagement`, `scroll`, `form_start`, `form_submit`, and `click` for host `franchisecefa.com` over `2026-05-01` through `2026-05-04`. | None for base traffic collection. |
| Franchise USA GA4 final lead collection | Partial | Controlled Form 1 and Form 2 tests on 2026-05-04 pushed helper events and dispatch events with clean attribution payloads; GA4 realtime had passed in the live main-conversion audit. | Re-run processed GA4 Data API reports after processing delay. |
| Franchise USA GA4 property settings | Verified | GA4 property `519783092` exists, timezone is `America/Los_Angeles`, and default currency is currently `CAD`. It is linked to Google Ads customers `3820636025` and `4159217891`. | Open question: confirm whether USA property currency should remain `CAD` or be changed to `USD` before reporting signoff. |
| Franchise USA Google Ads | Partial | Google Ads reporting confirms USA-related imported conversion actions exist in both linked accounts. The checked USA final actions still have `0` all conversions. | Decide which account and conversion action should be the USA bidding/primary action before activating final Google Ads helper-event tags. |
| Franchise USA Meta | Partial | USA dataset `1531247935333023` is now live through GTM Version `16`; old shared pixel `918227085392601` was removed from active USA WordPress header/body options; post-purge headless network check saw `1531247935333023` and zero old-dataset Meta requests. | Confirm Events Manager receipt and create/confirm USA-specific custom conversions / optimization event. |
| Gravity Forms Measurement Protocol | Pending | MP remains allowed only as an audit-only layer. | If tested, send `franchise_us_inquiry_submit_server_audit`; do not send a second `generate_lead`. Use lowercase `location_interest` and no PII/high-cardinality values. |

## 2026-05-04 GAConnector Cleanup Patch

What changed:

- The live franchise WPCode bridge now backfills existing Gravity Forms hidden attribution fields `14` through `30` from GAConnector cookies during `gform_pre_submission_1` and `gform_pre_submission_2`.
- Missing or placeholder values such as blank, `undefined`, `null`, and `(not set)` are filled before the entry is saved.
- `gclid` gets one special cleanup rule: when Google’s current `_gcl_aw` cookie is present, it wins over stale `gaconnector_gclid` and stale hidden field `29`.
- The patch does not change Synuma/SiteZeus/CRM delivery fields, form UI, location routing, GTM destination tags, GA4 settings, Google Ads settings, or Meta settings.

Live evidence:

| Site | Form | Entry | DataLayer event | Attribution result |
|---|---|---:|---|---|
| `franchise.cefa.ca` | Form `2` / Submit a Site | `46` | `real_estate_site_submit` | Saved and pushed `lc_source=qa_tracking`, `lc_medium=live_patch`, `lc_campaign=gaconnector_backfill_20260504`, `gclid=QA-FRCA-PATCH-SITE-20260504`, `ga_client_id=1065795917.1777927212`. |
| `franchisecefa.com` | Form `1` / Franchise Inquiry | `37` | `franchise_inquiry_submit` | Saved and pushed `lc_source=qa_tracking`, `lc_medium=live_patch`, `lc_campaign=gaconnector_backfill_20260504`, `gclid=QA-FRUS-PATCH-INQ-20260504`, `ga_client_id=1930300797.1777927657`. |
| `franchisecefa.com` | Form `2` / Submit a Site | `36` | `real_estate_site_submit` | Saved and pushed `lc_source=qa_tracking`, `lc_medium=live_patch`, `lc_campaign=gaconnector_backfill_20260504`, `gclid=QA-FRUS-PATCH-SITE-20260504`, `ga_client_id=1618510533.1777927481`. |

Interpretation: the earlier Canada stale-`gclid` issue and USA blank-attribution issue are fixed at the website/GF-entry/helper-payload level. Processed GA4 reporting still needs the normal reporting-delay recheck.

## 2026-05-04 Franchise USA Meta Dataset Split

What changed:

- USA GTM container `GTM-5LZMHBZL` was published as Version `16`: `CEFA Franchise USA Meta dataset split - 2026-05-04`.
- Active Meta base pixel tag `57` now initializes dataset `1531247935333023`.
- New host-scoped trigger `266` limits the USA Meta base pixel to `^(www\.)?franchisecefa\.com$`.
- New Meta standard `Lead` tags were added on the existing USA dispatch events:
  - Tag `267`: Form `1` / Franchise Inquiry, trigger `260`.
  - Tag `268`: Form `2` / Submit a Site, trigger `261`.
- The old shared Meta pixel `918227085392601` was removed from USA WordPress Insert Headers and Footers options `ihaf_insert_header` and `ihaf_insert_body`.

Verification:

| Check | Result |
|---|---|
| Public `gtm.js?id=GTM-5LZMHBZL` | Contains `1531247935333023`; zero active public-runtime occurrences of `918227085392601`. |
| Fresh Form 1/Form 2 HTML after WP Engine cache purge | Contains `GTM-5LZMHBZL`; zero HTML occurrences of `918227085392601`. |
| WordPress DB search | `wp db search 918227085392601 --all-tables` returned zero matches. |
| Fresh headless Chrome network check | Saw Meta config request for `1531247935333023`; saw zero Meta requests for `918227085392601`. |

Remaining Meta item: Events Manager must still be checked directly for dataset receipt and USA custom conversion / optimization-event setup.

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
| 1 | Re-run processed GA4 Data API reports for Canada and USA after the 2026-05-04 patched submissions process. | Pending | Browser/dataLayer/GF-entry evidence is fixed; processed reporting still lags. |
| 2 | Disable or prove audit-only the active USA Gravity Forms Google Analytics Form `1` feed. | Pending | This is now the main USA duplicate-source risk. |
| 3 | Confirm USA Google Ads bidding account and primary conversion action. | Open question | Both linked accounts contain USA-related actions; current checked actions have zero all conversions. |
| 4 | Confirm USA Meta Events Manager receipt/custom conversions for dataset `1531247935333023`. | Pending | USA is now separated in GTM/browser runtime; Meta UI/API signoff is still needed. |
| 5 | Confirm whether USA GA4 default currency should remain `CAD` or become `USD`. | Open question | Current property default is `CAD`; the Form 2 browser hit used `USD`. |
| 6 | Confirm Canada Meta custom conversions in Events Manager. | Pending | Browser receipt is verified, but Events Manager custom-conversion setup is not. |
| 7 | Make Canada Google Ads primary/secondary decision with the media owner. | Open question | Current primary action may not match the new helper-event path. |

## Guardrails

- Do not create duplicate final conversions.
- Do not activate Gravity Forms Measurement Protocol as a second `generate_lead` source.
- Do not send PII or high-cardinality values to GA4, Google Ads, Meta, or dataLayer.
- Do not overwrite business/CRM fields. For attribution-only hidden fields, backfill missing/placeholder values and only override `gclid` when the current Google `_gcl_aw` cookie proves the latest click ID.
- Do not replace Synuma, SiteZeus, CRM delivery, Gravity Forms UI, or agency-owned business logic.
- Keep website events neutral and let GTM map them to platform events.
