# Live Conversion Tracking Recheck

Last updated: 2026-05-04

Update note: this read-only recheck was followed by controlled live Franchise Canada and Franchise USA submissions later on 2026-05-04. It was then followed by a parent plugin deployment, franchise GAConnector cleanup patch, Franchise USA GTM Version `16` Meta dataset split to `1531247935333023`, and Franchise USA GTM Version `17` legacy micro/click cleanup. For the current main conversion event signoff, use [Live main conversion event audit, 2026-05-04](./live-main-conversion-event-audit-2026-05-04.md).

## Purpose

Re-check the live conversion tracking state after confirming WP Engine SSH/WP-CLI access for all three sites.

No live WordPress plugin update, GTM publish, Google Ads mutation, GA4 setting change, or Meta change was made by this recheck.

## Summary

| Site | Status | Main finding |
|---|---|---|
| Parent `cefa.ca` | Mostly good | GTM now points `school_inquiry_submit` to existing Google Ads `Inquiry Submit_ollo`; later on 2026-05-04 the live plugin was updated from `0.4.1` to `0.4.3`. |
| Franchise Canada `franchise.cefa.ca` | Partially verified | Site loads the franchise bridge and GTM; GA4 has at least one helper-plugin `generate_lead`; no Gravity Forms Google Analytics feed was found. |
| Franchise USA `franchisecefa.com` | Historical snapshot, superseded | This early recheck found the site loaded the franchise bridge and GTM, but GA4 Data API returned no rows for the target franchise events; an active Gravity Forms Google Analytics feed existed for Form `1`. Later live QA passed the helper path, GTM Version `16` moved USA Meta to dataset `1531247935333023`, and GTM Version `17` paused old active micro/click tags. |

## Parent `cefa.ca`

### Runtime Checks

| Check | Result |
|---|---|
| WP-CLI siteurl | `https://cefa.ca` |
| Active conversion plugin | Initially `cefa-conversion-tracking` `0.4.1`; later updated to `0.4.3` on 2026-05-04. |
| Repo package ready | `0.4.3` |
| Gravity Forms | active `2.10.1` |
| School Manager | active `1.0.18` |
| MCP Adapter | active `0.5.0` |
| Public HTML GTM container | `GTM-NZ6N7WNC` |
| Public HTML helper asset | Initially `cefa-conversion-tracking.js?ver=0.4.1`; post-deploy sample shows `cefa-conversion-tracking.js?ver=0.4.3`. |

### GTM / Google Ads Label Check

Public `gtm.js` check for `GTM-NZ6N7WNC`:

| Marker | Result |
|---|---|
| `AW-802334988` | Present |
| `G-T65G018LYB` | Present |
| Meta pixel `918227085392601` | Present |
| Correct Google Ads label `cFt-CMrLufgCEIzSyv4C` | Present |
| Old wrong label `5_KbCJO3j_gCEIzSyv4C` | Not present |

Interpretation:

- The Google Ads label correction is live.
- The parent helper event still uses the clean website event `school_inquiry_submit`.
- Google Ads is not using a new conversion action; it is using the existing `Inquiry Submit_ollo` label.

### GA4 Data API

Property: `267558140` / `Main Site - GA4`

Date range: `2026-05-01` to `2026-05-04`

| Event | Tracking source | Form ID | Event count | Key events |
|---|---|---|---:|---:|
| `parent_inquiry_cta_click` | `helper_plugin` | `4` | `734` | `0` |
| `form_submit_click` | `helper_plugin` | `4` | `418` | `0` |
| `find_a_school_click` | `helper_plugin` | `(not set)` / blank | `281` | `281` |
| `validation_error` | `helper_plugin` | `4` | `147` | `0` |
| `generate_lead` | `helper_plugin` | `4` | `139` | `139` |
| `email_click` | `helper_plugin` | `(not set)` / blank | `49` | `49` |
| `phone_click` | `helper_plugin` | `(not set)` / blank | `18` | `18` |

Interpretation:

- Parent helper-plugin events are reaching GA4.
- `generate_lead` is processing as the key event for the parent submit path.
- Micro events are visible in GA4 reporting; they remain outside Google Ads bidding unless explicitly changed.

### BigQuery GA4 Export

Dataset: `marketing-api-488017.analytics_267558140.events_*`

Table suffixes checked: `20260501` through `20260504`

| Event | Tracking source | Export rows | Missing `event_id` | `event_id = school_selected_id` |
|---|---|---:|---:|---:|
| `parent_inquiry_cta_click` | `helper_plugin` | `645` | `0` | `0` |
| `form_submit_click` | `helper_plugin` | `381` | `0` | `0` |
| `validation_error` | `helper_plugin` | `132` | `0` | `0` |
| `generate_lead` | `helper_plugin` | `121` | `0` | `1` |

Interpretation:

- BigQuery confirms helper events are exporting.
- The one historical `generate_lead` row where `event_id` equals `school_selected_id` is still present in the export window.
- Repo plugin `0.4.3` guards against that failure mode and was deployed later on 2026-05-04.

### Gravity Forms Add-On Feed Check

Table checked: `wp_gf_addon_feed`

| Feed | Result |
|---|---|
| Gravity Forms Google Analytics feed | None found on parent |
| Other feed found | `gravityformsmailchimp`, Form `1`, active |

Interpretation:

- Parent is not currently using the Gravity Forms Google Analytics Add-On as a competing final conversion source.
- Parent final browser source remains the CEFA helper plugin plus GTM.

## Franchise Canada `franchise.cefa.ca`

### Runtime Checks

| Check | Result |
|---|---|
| WP-CLI siteurl | `https://franchise.cefa.ca` |
| Franchise control plugin | active `0.1.12` |
| Gravity Forms | active `2.10.1` |
| MCP Adapter | active `0.5.0` |
| Public HTML GTM container | `GTM-TPJGHFS` |
| Public HTML bridge markers | `franchise_inquiry_submit`, `real_estate_site_submit` present |

### GTM / GA4 Public Markers

Public `gtm.js` check for `GTM-TPJGHFS` found:

- `franchise_inquiry_submit`
- `real_estate_site_submit`
- `generate_lead`
- `G-6EMKPZD7RD`
- `AW-802334988`
- `AW-11088792613`
- Meta pixel `918227085392601`

### GA4 Data API

Property: `259747921` / `CEFA Franchise`

Date range: `2026-05-01` to `2026-05-04`

| Event | Tracking source | Form ID | Event count | Key events |
|---|---|---|---:|---:|
| `generate_lead` | `(not set)` | `(not set)` | `3` | `3` |
| `generate_lead` | `helper_plugin` | `1` | `1` | `1` |

### Gravity Forms Add-On Feed Check

No active Gravity Forms add-on feed rows were found in `wp_gf_addon_feed`.

Interpretation:

- Canada has bridge and GTM markers live.
- Canada has at least one processed helper-plugin `generate_lead`.
- Canada still needs a controlled post-live QA pass before calling franchise tracking complete.

## Franchise USA `franchisecefa.com`

### Runtime Checks

| Check | Result |
|---|---|
| WP-CLI siteurl | `https://franchisecefa.com` |
| Franchise control plugin | active `0.1.13` |
| Gravity Forms | active `2.10.1` |
| Gravity Forms Google Analytics Add-On | active `2.4.1` |
| MCP Adapter | active `0.5.0` |
| Public HTML GTM container | `GTM-5LZMHBZL` |
| Public HTML bridge markers | `franchise_inquiry_submit`, `real_estate_site_submit` present |

### GTM / GA4 Public Markers

Public `gtm.js` check for `GTM-5LZMHBZL` found:

- `franchise_inquiry_submit`
- `real_estate_site_submit`
- `generate_lead`
- `G-YL1KQPWV0M`
- `AW-802334988`
- `AW-11088792613`
- Meta pixel `918227085392601`

Superseded note: the Meta pixel marker above was true for this early read-only recheck. Later on 2026-05-04, USA GTM Version `16` moved the active USA Meta runtime to dataset `1531247935333023`; Version `17` retained that dataset and paused old active micro/click tags. Post-purge/runtime checks found zero active public-runtime or page-HTML occurrences of `918227085392601` on the USA form pages.

### GA4 Data API

Property: `519783092` / `CEFA Franchise - USA.`

Date range: `2026-05-01` to `2026-05-04`

Result:

- No rows returned for `generate_lead`, `franchise_inquiry_submit`, `real_estate_site_submit`, `cefa_franchise_us_inquiry_dispatch`, or `cefa_franchise_us_site_dispatch`.

### Gravity Forms Add-On Feed Check

Table checked: `wp_gf_addon_feed`

| Feed ID | Form ID | Add-on slug | Active |
|---:|---:|---|---:|
| `1` | `1` | `gravityformsgoogleanalytics` | `1` |

Interpretation:

- USA bridge and GTM markers are present publicly.
- Processed GA4 report rows are not visible for the target USA events in this date window.
- The active Gravity Forms Google Analytics feed for USA Form `1` is a potential alternate/duplicate source and needs a dedicated USA audit before final signoff.

## Current Recommendation

1. Parent: run one controlled mobile Form `4` submission after deployment.
2. Parent: verify the network request uses `AW-802334988/cFt-CMrLufgCEIzSyv4C`.
3. Parent: confirm the new submitted `event_id` does not equal `school_selected_id`.
4. Franchise Canada: re-run processed GA4 reporting after the patched Form `2` submission has processed.
5. Franchise USA: audit the active Gravity Forms Google Analytics feed before deciding whether to keep, disable, or convert it to audit-only.
6. Franchise USA: re-run processed GA4 reporting after the patched Form `1` and Form `2` submissions have processed.

## Signoff State

| Site | Browser helper source | GTM public mapping | GA4 processed evidence | Ads final mapping | Main blocker |
|---|---|---|---|---|---|
| Parent | Pass | Pass | Pass | Pass for existing `Inquiry Submit_ollo` label | Plugin `0.4.3` is deployed; post-change mobile controlled submit still needed. |
| Franchise Canada | Pass markers | Pass markers | Partial | Not fully signed off | Processed reporting after patched submission still pending. |
| Franchise USA | Pass markers | Pass markers | Realtime/live helper passed after patch; processed rows pending | Not fully signed off | Active GF GA feed and processed GA4 recheck still pending. |
