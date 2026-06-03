# Parent Current State And Remaining Work

Last updated: 2026-05-05

## Purpose

This file summarizes what is done and what is still left for parent `cefa.ca` conversion tracking. It is limited to the parent enrollment/inquiry path and does not cover franchise Canada or franchise USA except where cross-property guardrails apply.

## Scope

| Field | Value |
|---|---|
| Workstream | Conversion tracking |
| Property | `cefa.ca` |
| Primary form | Gravity Forms Form `4` |
| Primary website event | `school_inquiry_submit` |
| Active GTM container | `GTM-NZ6N7WNC` |
| GA4 property | `properties/267558140` / `Main Site - GA4` |
| Live writes made by this update | GTM version `7` published earlier; WordPress plugin `cefa-conversion-tracking` updated to `0.4.3` on 2026-05-04. On 2026-05-05, emergency GTM version `9` paused Custom HTML tags after a loop-risk incident. No Google Ads, GA4, or Meta platform setting writes were made in this documentation update. |

## Current Verified Status

| Area | Status | Current state |
|---|---|---|
| Website-side final event | Verified | Parent final event is `school_inquiry_submit`, emitted by the CEFA Conversion Tracking plugin after confirmed Form 4 success. |
| Final source of truth for browser conversion | Verified | Helper-plugin dataLayer event is the final browser source, not a Gravity Forms Google Analytics Add-On event or thank-you pageview. |
| GTM container | Verified with caution | Live sampled inquiry and thank-you pages load `GTM-NZ6N7WNC`; sampled HTML did not show old `GTM-PPV9ZRZ`. Public live GTM version `9` currently keeps Meta Tags `39`/`40` paused until a narrow restore publish is made. |
| Helper plugin render | Verified | Live sampled inquiry and thank-you pages render `cefa-conversion-tracking` config, Form 4 field map, attribution map, token endpoints, and tracked micro-event names. |
| Event identity | Verified | Approved event identity is `event_id`; do not use school UUID, school slug, program ID, or location ID as `event_id`. |
| School/program metadata | Verified | Parent tracking contract reads Field 32 values: `32.1` school UUID, `32.2` program ID, `32.3` days per week, `32.4` event ID, `32.5` school slug, `32.6` school name, `32.7` program name. |
| Attribution bridge | Verified | Parent tracking contract uses fields `35` through `46` for UTM/click-ID/first-touch handoff. |
| Direct thank-you protection | Verified | The live thank-you page renders plugin token logic; prior QA confirms direct thank-you visits/reloads do not create final conversions without a valid token. |
| GA4 export helper evidence | Verified | BigQuery last-seven-day check on 2026-05-04 found `127` helper-plugin `generate_lead` events, `135` helper-plugin `validation_error` events, and `0` duplicate helper-plugin `generate_lead` event-ID groups. Latest exported event date in that check was 2026-05-02. |
| GA4 custom definitions | Verified from existing repo docs | Parent helper low-cardinality dimensions are registered in GA4 property `267558140`. |
| GA4 key event | Verified from existing repo docs | `generate_lead` is a GA4 key event; `validation_error` is not. |
| Google Ads link | Verified from existing repo docs | GA4 property `267558140` is linked to Google Ads customer `4159217891`. |
| Google Ads direct conversion label | Verified | Live GTM version `7` uses label `cFt-CMrLufgCEIzSyv4C`, which maps to the existing `Inquiry Submit_ollo` action. No new Google Ads conversion action was created. |
| Live plugin package version | Verified | WP-CLI reports `cefa-conversion-tracking` active `0.4.3`; the 2026-05-05 Tag Assistant preview confirms the plugin emits the final `school_inquiry_submit` payload with clean Form 4 metadata. |

## Done

- Parent final event contract is defined: one successful Form 4 submission should produce one `school_inquiry_submit`.
- The helper plugin is active on live `cefa.ca` and renders on the sampled inquiry and thank-you pages.
- The active live GTM path is `GTM-NZ6N7WNC`.
- The old parent GTM path `GTM-PPV9ZRZ` is treated as archived/reference-only and was not present in sampled live HTML.
- Gravity Forms Google Analytics Add-On is not the final conversion source.
- The event payload contract separates `event_id`, school ID, school slug, school name, program ID, program name, and days per week.
- Attribution persistence is handled by the CEFA-owned bridge into Form 4 fields `35` through `46`.
- Micro-events are available website-side: `parent_inquiry_cta_click`, `find_a_school_click`, `phone_click`, `email_click`, `form_start`, `form_submit_click`, and `validation_error`.
- BigQuery export evidence shows helper-plugin GA4 `generate_lead` and `validation_error` rows with no duplicate helper `generate_lead` event IDs in the latest checked seven-day export window.
- GA4 custom dimensions exist for the parent helper payload.
- Parent GTM live version `7` mapped `school_inquiry_submit` to GA4 `generate_lead`, Meta `Inquiry Submit`, and the existing Google Ads `Inquiry Submit_ollo` action. Emergency public live version `9` now keeps Meta Tags `39`/`40` paused; Tag Assistant preview confirms they work when reopened, but a narrow Meta-only restore publish is still required.
- A 2026-05-04 GTM publish corrected the direct Google Ads helper-event tag from the `Contact Form Submit_ollo` label to the existing `Inquiry Submit_ollo` label.
- Repo plugin `0.4.3` now rejects school/program/day metadata values if they appear in the event ID field, after BigQuery showed one helper `generate_lead` row where `event_id` equaled `school_selected_id`.
- Live `cefa.ca` now runs plugin `0.4.3`; the sampled inquiry page renders `GTM-NZ6N7WNC` and helper asset `cefa-conversion-tracking.js?ver=0.4.3`.
- Local-listing UTM rules for GBP/Yelp have been documented under the naming-convention workstream.

## Left

| Priority | Status | Item | Why it matters |
|---|---|---|---|
| 1 | Pending | Publish only Meta Tags `39`/`40` after confirming Tags `66`/`67`/`68` stay paused. | Restores parent Meta browser tracking without reintroducing the GA4 Custom HTML loop pattern. |
| 2 | Pending | Run one controlled Form 4 submission after the Meta-only restore publish. | Confirms the final event still produces GA4, Ads, and Meta hits after live publish. |
| 3 | Pending | Run one mobile browser Form 4 submission QA after plugin/GTM updates. | Mobile is the one remaining parent production QA scenario listed as open. |
| 4 | Pending | Verify one post-change Ads request uses `AW-802334988/cFt-CMrLufgCEIzSyv4C`. | Confirms the existing `Inquiry Submit_ollo` learning path is receiving the helper event. |
| 5 | Pending | Confirm Meta Events Manager custom conversion and optimization-event status. | Meta delivery/learning depends on the correct event and dataset configuration. |
| 6 | Pending | Reconcile `school_inquiry_submit` through GTM, GA4, Google Ads, Meta, and BigQuery after the latest production traffic window. | Confirms the full path, not just browser and GA4 export evidence. |
| 7 | Pending | Refresh or reconnect current parent business-truth inquiry marts after 2026-03-29. | Platform/GA4 conversions are not final inquiry truth until CRM/KinderTales/collector-backed reporting is current. |
| 8 | Pending | Review and archive obsolete old GTM tags/triggers only after proving they are not used by production. | Prevents accidental deletion of still-needed reporting or legacy references. |
| 9 | Pending | Review old GA4 key events/custom dimensions after production is stable. | Cleanup should not break historical reporting or Ads imports. |
| 10 | Future | Build Phase 1B server-side/audit path: collector, Meta CAPI, Measurement Protocol audit-only, and then sGTM. | Strengthens attribution and resilience after browser tracking and business truth are stable. |
| 11 | Future | Build machine-readable school/program crosswalks under `data/reference/`. | Needed for durable joins across GA4, BigQuery, GBP, CRM, ads, and reporting. |

## Current Guardrails

- Do not reactivate the Gravity Forms Google Analytics Add-On as a second final conversion source.
- Do not map final parent conversions from `GTM-PPV9ZRZ`.
- Do not use thank-you pageviews as the final lead source.
- Do not register high-cardinality fields such as full URLs, referrers, click IDs, or `event_id` as GA4 custom dimensions unless there is a specific governed reason.
- Do not put micro-conversions into Google Ads bidding unless CEFA explicitly changes that launch rule.
- Do not treat GA4/platform conversions as final business truth until current CRM/KinderTales/collector-backed inquiry data is refreshed and reconciled.
- Do not publish GTM Custom HTML tags that call `gtag()` for GA4 events. GA4 event delivery must use native GA4 Event tags or another non-looping pattern.

## Evidence Checked In This Update

- Live HTML sample: `https://cefa.ca/submit-an-inquiry-today/?location=abbotsford-highstreet`
- Live HTML sample: `https://cefa.ca/thank-you/?location=abbotsford-highstreet&inquiry=true`
- WP-CLI parent plugin check: `cefa-conversion-tracking,active,0.4.3`
- Live HTML sample after deploy: `GTM-NZ6N7WNC` and `cefa-conversion-tracking.js?ver=0.4.3`
- BigQuery GA4 export: `marketing-api-488017.analytics_267558140.events_*`
- Google / GTM / Ads API audit:
  - `docs/10-conversion-tracking/parent-google-gtm-ads-signoff-2026-05-04.md`
- Tag Assistant preview and Meta restore plan:
  - `docs/10-conversion-tracking/parent-tag-assistant-preview-and-meta-restore-plan-2026-05-05.md`
- Existing parent docs:
  - `docs/parent-production-cutover-checklist.md`
  - `docs/live-conversion-tracking-status-2026-05-01.md`
  - `docs/10-conversion-tracking/business-truth-and-tracking-data-gaps-2026-05-03.md`

## Next Action Recommendation

Do the remaining parent work in this order:

1. Publish only parent Meta Tags `39`/`40`, while keeping Tags `66`/`67`/`68` paused.
2. Run one controlled Form 4 QA and one mobile Form 4 QA.
3. Verify the post-change Ads request uses `AW-802334988/cFt-CMrLufgCEIzSyv4C`.
4. Confirm Meta custom conversion / optimization status.
5. Refresh the parent business-truth inquiry marts and reconcile against helper events.
6. Only then clean old GTM/GA4 artifacts and start Phase 1B server-side work.
