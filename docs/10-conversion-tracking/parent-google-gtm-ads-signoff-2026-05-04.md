# Parent Google / GTM / Ads Signoff

Last updated: 2026-05-04

## Purpose

Document the current parent `cefa.ca` Google-side implementation state after the live-domain cutover.

This file is based on platform API checks, one approved GTM publish, and a repo-side plugin safeguard. No Google Ads conversion action was created, renamed, or mutated. No GA4 setting change or Meta change was made by this update. Later on 2026-05-04, the parent WordPress plugin was deployed to live as `0.4.3`.

## Scope

| Field | Value |
|---|---|
| Property | Parent `cefa.ca` |
| Website event | `school_inquiry_submit` |
| Active GTM container observed on live page | `GTM-NZ6N7WNC` |
| Active GTM live version after correction | `7` / `CEFA parent Ads label correction - Inquiry Submit_ollo - 2026-05-04` |
| GA4 property | `267558140` / `Main Site - GA4` |
| Google Ads account | `4159217891` / `CEFA $3000` |
| Meta pixel seen in GTM | `918227085392601` |
| Live plugin asset observed | Initially `cefa-conversion-tracking.js?ver=0.4.1`; post-deploy sample shows `cefa-conversion-tracking.js?ver=0.4.3` |
| Repo/live plugin after deployment | `0.4.3` |

## Current Live Page Evidence

Read-only HTML checks on:

- `https://cefa.ca/submit-an-inquiry-today/?location=abbotsford-highstreet`
- `https://cefa.ca/thank-you/?location=abbotsford-highstreet&inquiry=true`

Verified:

- Live pages load `GTM-NZ6N7WNC`.
- Initial read-only sample loaded `cefa-conversion-tracking.js?ver=0.4.1`; post-deploy sample loaded `cefa-conversion-tracking.js?ver=0.4.3`.
- The old parent container `GTM-PPV9ZRZ` was not observed in the sampled live HTML.

## GTM Live Container Audit

Source: Google Tag Manager API, account `4591216764`, container `250451797`, live version `7`.

Live version name:

`CEFA parent Ads label correction - Inquiry Submit_ollo - 2026-05-04`

| Item | Count |
|---|---:|
| Tags | 18 |
| Triggers | 11 |
| Variables | 36 |
| Workspaces | 1 |

### Final Submit Mapping

| Destination | GTM tag | Trigger | Current status |
|---|---|---|---|
| GA4 | `CEFA Phase 1A - GA4 generate_lead - school_inquiry_submit` | Custom event `school_inquiry_submit` | Working as the GA4 parent lead event. |
| Google Ads base tag | `CEFA Phase 1A - Google Tag - Ads Parent AW-802334988` | All pages | Present. |
| Google Ads conversion tag | `CEFA Phase 1A - Google Ads Parent Inquiry Submit - Inquiry Submit_ollo` | Custom event `school_inquiry_submit` | Corrected to the existing `Inquiry Submit_ollo` conversion label. |
| Meta base pixel | `CEFA Phase 1A - Meta Base Pixel - parent` | All pages | Present with pixel `918227085392601`. |
| Meta lead event | `CEFA Phase 1A - Meta Inquiry Submit continuity - school_inquiry_submit` | Custom event `school_inquiry_submit` | Present as `trackCustom('Inquiry Submit')` with `eventID={{DLV - event_id}}`. |

### GA4 Submit Payload

The GA4 `generate_lead` tag sends these parameters from the helper-plugin payload:

- `event_id`
- `form_id`
- `form_family`
- `lead_type`
- `lead_intent`
- `school_selected_id`
- `school_selected_slug`
- `school_selected_name`
- `school_landing_id`
- `school_landing_slug`
- `school_match_status`
- `program_id`
- `program_name`
- `days_per_week`
- `inquiry_success`
- `inquiry_success_url`
- `page_context`
- `tracking_source`
- `value=150`
- `currency=CAD`

### Micro-Conversion Mapping

The live container has GA4 tags for:

- `phone_click`
- `email_click`
- `find_a_school_click`
- `parent_inquiry_cta_click`
- `form_start`
- `form_submit_click`
- `validation_error`

These are mapped to GA4 only. They should stay out of Google Ads bidding at launch unless CEFA explicitly changes the rule.

### GTM Cleanup Notes

- The active `school_inquiry_submit` trigger is still named `CEFA POC - Event - school_inquiry_submit`, but it correctly matches the event name `school_inquiry_submit`.
- Staging-only POC helper/console tags remain in the container. The helper tag is hostname-gated to `cefamain.kinsta.cloud`, so it should not create the parent live event on `cefa.ca`.
- Staging/POC naming cleanup can wait until after post-change QA; do not do cleanup-only publishes while the conversion path is still being validated.

## Google Ads Label Correction Published

The parent helper-event Ads tag was corrected in GTM live version `7`.

| Field | Before | After |
|---|---|---|
| Website/dataLayer event | `school_inquiry_submit` | `school_inquiry_submit` |
| Google Ads conversion ID | `802334988` | `802334988` |
| Google Ads conversion label | `5_KbCJO3j_gCEIzSyv4C` | `cFt-CMrLufgCEIzSyv4C` |
| Google Ads action | `Contact Form Submit_ollo` | `Inquiry Submit_ollo` |
| Value | `150` | `150` |
| Currency | `CAD` | `CAD` |

Google Ads API tag-snippet lookup shows:

| Conversion label | Google Ads action it belongs to | Current helper-event usage |
|---|---|---|
| `5_KbCJO3j_gCEIzSyv4C` | `Contact Form Submit_ollo` | No longer used by the live parent helper-event Ads tag. |
| `cFt-CMrLufgCEIzSyv4C` | `Inquiry Submit_ollo` | Now used by the live parent helper-event Ads tag. |

This preserves the existing Google Ads `Inquiry Submit_ollo` conversion action and its learning surface. No new Google Ads conversion action was created.

Public `gtm.js` verification after publish:

| Check | Result |
|---|---|
| `AW-802334988` present | Yes |
| Correct label `cFt-CMrLufgCEIzSyv4C` present | Yes |
| Old label `5_KbCJO3j_gCEIzSyv4C` present | No |

## Google Ads Conversion Action Status

Source: Google Ads API, customer `4159217891`.

| Action | ID | Type | Status | Primary | Include in conversions | Value | Currency | Notes |
|---|---:|---|---|---:|---:|---:|---|---|
| `Inquiry Submit_ollo` | `789472714` | `WEBPAGE` | `ENABLED` | `true` | `true` | `150` | `CAD` | Intended parent lead bidding action. Label is `cFt-CMrLufgCEIzSyv4C`. |
| `Contact Form Submit_ollo` | `788781971` | `WEBPAGE` | `ENABLED` | `true` | `false` | `100` | `CAD` | Previously used by the live helper-event Ads tag before GTM version `7`; no longer the helper-event Ads label. |
| `generate_lead (GA4)` | `6540439360` | `UNKNOWN` | `ENABLED` | `false` | `false` | `1` | `CAD` | GA4-imported lead action. Secondary/reporting only. |
| `Phone Click_ollo` | `789475090` | `WEBPAGE` | `ENABLED` | `true` | `false` | `10` | `CAD` | Micro/secondary; not included in conversions metric. |
| `Email Click_ollo` | `789488589` | `WEBPAGE` | `ENABLED` | `true` | `false` | `10` | `CAD` | Micro/secondary; not included in conversions metric. |

Last-30-day Google Ads action counts showed historical volume on `Inquiry Submit_ollo`, but the API returned no rows for `Inquiry Submit_ollo`, `Contact Form Submit_ollo`, or `generate_lead (GA4)` between 2026-05-01 and 2026-05-04. Treat that recent-window result as inconclusive because conversion lag and traffic/ad-click conditions may apply.

## GA4 And BigQuery Evidence

Source: GA4 Data API for `properties/267558140`, date range 2026-05-01 to 2026-05-04.

| Event | Tracking source | Form ID | Event count | Key events |
|---|---|---|---:|---:|
| `generate_lead` | `helper_plugin` | `4` | `133` | `133` |
| `validation_error` | `helper_plugin` | `4` | `138` | `0` |
| `form_submit_click` | `helper_plugin` | `4` | `395` | `0` |
| `parent_inquiry_cta_click` | `helper_plugin` | `4` | `698` | `0` |
| `find_a_school_click` | `helper_plugin` | not set / blank | `266` | `266` |
| `email_click` | `helper_plugin` | not set / blank | `46` | `46` |
| `phone_click` | `helper_plugin` | not set / blank | `17` | `17` |

Source: BigQuery GA4 export `marketing-api-488017.analytics_267558140.events_*`, table suffixes `20260501` through `20260504`.

| Check | Result |
|---|---:|
| Helper-plugin `generate_lead` rows exported | `121` |
| Missing helper `event_id` values | `0` |
| Duplicate helper `event_id` rows | `0` |
| Rows where `event_id` equals `school_selected_id` | `1` |

The one `event_id = school_selected_id` row occurred on `event_date=20260503`, timestamp `2026-05-04 05:36:13 UTC`, for `new-westminster-downtown`.

## Repo Implementation Added In This Update

The repo plugin was bumped to `0.4.3` and now rejects an event ID candidate if it equals one of the configured form metadata values, including Field 32 school/program/day values.

Why this was added:

- The canonical rule is that `event_id` is submission-scoped.
- `school_selected_id`, school slug, program ID, program name, and days are metadata.
- If Form 4 field `32.4` is ever prefilled incorrectly with a school/program/day value, the plugin should generate/persist a fresh event ID instead of accepting that value.

The `0.4.3` safeguard was deployed later on 2026-05-04. WP-CLI reports `cefa-conversion-tracking,active,0.4.3`, and sampled live HTML loads `cefa-conversion-tracking.js?ver=0.4.3`.

## Signoff Status

| Area | Status | Reason |
|---|---|---|
| Website-side dataLayer event | Pass | `school_inquiry_submit` is live and GA4 receives helper-plugin `generate_lead` rows. |
| GA4 mapping | Pass with cleanup note | Main submit and micro events are mapped. Some old/non-helper form events remain in GA4 and should not be cleaned until after platform signoff. |
| Google Ads direct conversion mapping | Pass | Live GTM version `7` uses the existing `Inquiry Submit_ollo` label `cFt-CMrLufgCEIzSyv4C` on the `school_inquiry_submit` trigger. |
| Google Ads bidding action settings | Pass structurally | `Inquiry Submit_ollo` is enabled, primary, included, and valued at `150 CAD`; the GTM tag must point to it. |
| Meta browser mapping | Partial | GTM has pixel and lead-event tags with matching event ID, but Events Manager/custom-conversion optimization still needs platform verification. |
| Event ID lifecycle | Partial | Mostly clean in BigQuery, but one exported row reused school ID as event ID. Repo/live plugin `0.4.3` now guards against this; post-change controlled submit QA is still pending. |

## Recommended Next Changes

Remaining next changes:

1. Run one controlled parent Form 4 submission after the plugin update.
2. Verify in browser/network that the Ads request uses `AW-802334988/cFt-CMrLufgCEIzSyv4C`.
3. Re-check GA4 and BigQuery after processing delay.
4. Verify Meta Events Manager receives the parent custom event with matching `eventID`.

Do not change Google Ads primary/secondary settings yet. The current `Inquiry Submit_ollo` action remains the parent bidding action; GTM now fires its label from the helper-event path.
