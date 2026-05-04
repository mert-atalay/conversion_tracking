# Parent Google / GTM / Ads Signoff

Last updated: 2026-05-04

## Purpose

Document the current parent `cefa.ca` Google-side implementation state after the live-domain cutover.

This file is based on read-only checks plus a repo-side plugin safeguard. No live GTM publish, Google Ads mutation, GA4 setting change, WordPress deployment, or Meta change was made by this update.

## Scope

| Field | Value |
|---|---|
| Property | Parent `cefa.ca` |
| Website event | `school_inquiry_submit` |
| Active GTM container observed on live page | `GTM-NZ6N7WNC` |
| GA4 property | `267558140` / `Main Site - GA4` |
| Google Ads account | `4159217891` / `CEFA $3000` |
| Meta pixel seen in GTM | `918227085392601` |
| Live plugin asset observed | `cefa-conversion-tracking.js?ver=0.4.1` |
| Repo plugin after this update | `0.4.3` |

## Current Live Page Evidence

Read-only HTML checks on:

- `https://cefa.ca/submit-an-inquiry-today/?location=abbotsford-highstreet`
- `https://cefa.ca/thank-you/?location=abbotsford-highstreet&inquiry=true`

Verified:

- Live pages load `GTM-NZ6N7WNC`.
- Live pages load `cefa-conversion-tracking.js?ver=0.4.1`.
- The old parent container `GTM-PPV9ZRZ` was not observed in the sampled live HTML.

## GTM Live Container Audit

Source: Google Tag Manager API, account `4591216764`, container `250451797`, live version `5`.

Live version name:

`CEFA Phase 1A micro-conversion activation - 2026-04-25`

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
| Google Ads conversion tag | `CEFA Phase 1A - Google Ads Parent Inquiry Submit - candidate label` | Custom event `school_inquiry_submit` | Present, but label mismatch found. See critical finding below. |
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
- Rename/cleanup can wait until after the Ads label correction and post-change QA; do not risk a cleanup-only publish before the critical conversion path is fixed.

## Critical Google Ads Finding

The live GTM Google Ads conversion tag for parent inquiry currently uses:

| Field | Current value |
|---|---|
| Conversion ID | `802334988` |
| Conversion label in GTM | `5_KbCJO3j_gCEIzSyv4C` |
| Value | `150` |
| Currency | `CAD` |

Google Ads API tag-snippet lookup shows:

| Conversion label | Google Ads action it belongs to |
|---|---|
| `5_KbCJO3j_gCEIzSyv4C` | `Contact Form Submit_ollo` |
| `cFt-CMrLufgCEIzSyv4C` | `Inquiry Submit_ollo` |

This means the GTM tag name says parent inquiry, but the actual direct Google Ads conversion label is currently the `Contact Form Submit_ollo` label.

## Google Ads Conversion Action Status

Source: Google Ads API, customer `4159217891`.

| Action | ID | Type | Status | Primary | Include in conversions | Value | Currency | Notes |
|---|---:|---|---|---:|---:|---:|---|---|
| `Inquiry Submit_ollo` | `789472714` | `WEBPAGE` | `ENABLED` | `true` | `true` | `150` | `CAD` | Intended parent lead bidding action. Label is `cFt-CMrLufgCEIzSyv4C`. |
| `Contact Form Submit_ollo` | `788781971` | `WEBPAGE` | `ENABLED` | `true` | `false` | `100` | `CAD` | Current GTM helper-event direct Ads label resolves here. Not included in conversions metric. |
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

Live WordPress still appears to serve plugin asset `0.4.1` from sampled pages. The `0.4.3` safeguard is not live until the updated plugin is deployed.

## Signoff Status

| Area | Status | Reason |
|---|---|---|
| Website-side dataLayer event | Pass | `school_inquiry_submit` is live and GA4 receives helper-plugin `generate_lead` rows. |
| GA4 mapping | Pass with cleanup note | Main submit and micro events are mapped. Some old/non-helper form events remain in GA4 and should not be cleaned until after platform signoff. |
| Google Ads direct conversion mapping | Fail | The live helper-event Ads tag uses the `Contact Form Submit_ollo` label, not the intended `Inquiry Submit_ollo` label. |
| Google Ads bidding action settings | Pass structurally | `Inquiry Submit_ollo` is enabled, primary, included, and valued at `150 CAD`; the GTM tag must point to it. |
| Meta browser mapping | Partial | GTM has pixel and lead-event tags with matching event ID, but Events Manager/custom-conversion optimization still needs platform verification. |
| Event ID lifecycle | Partial | Mostly clean in BigQuery, but one exported row reused school ID as event ID. Repo `0.4.3` now guards against this; live deployment still pending. |

## Recommended Next Changes

These require explicit approval before live action:

1. Publish a GTM correction that changes `CEFA Phase 1A - Google Ads Parent Inquiry Submit - candidate label` from label `5_KbCJO3j_gCEIzSyv4C` to `cFt-CMrLufgCEIzSyv4C`.
2. Rename the tag from candidate wording to a final name after the label is corrected.
3. Deploy plugin `0.4.3` to live `cefa.ca`.
4. Run one controlled parent Form 4 submission after the GTM and plugin updates.
5. Verify in browser/network that the Ads request uses `AW-802334988/cFt-CMrLufgCEIzSyv4C`.
6. Re-check GA4 and BigQuery after processing delay.
7. Verify Meta Events Manager receives the parent custom event with matching `eventID`.

Do not change Google Ads primary/secondary settings yet. The current `Inquiry Submit_ollo` action is structurally the right parent bidding action; the immediate issue is that GTM is not firing its label from the helper-event path.
