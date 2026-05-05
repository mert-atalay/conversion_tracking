# Parent Tag Assistant Preview And Meta Restore Plan - 2026-05-05

Status: verified from Tag Assistant export, live WP-CLI, and public GTM payload.

Property: parent `cefa.ca`

Evidence file:

- `/Users/matthewbison/Downloads/tag_assistant_cefa_ca_2026_05_05.json`

## Current State

Live WordPress plugin state:

- `cefa-conversion-tracking`: active, version `0.4.3`
- Gravity Forms: active, version `2.10.1`
- CEFA School Manager: active, version `1.0.18`

Public live GTM state:

- Account: `4591216764`
- Container: `250451797`
- Public ID: `GTM-NZ6N7WNC`
- Public live version: `9`

In public live GTM version `9`, these tags remain paused:

- Tag `39`: `CEFA Phase 1A - Meta Base Pixel - parent`
- Tag `40`: `CEFA Phase 1A - Meta Inquiry Submit continuity - school_inquiry_submit`
- Tag `66`: `CEFA Phase 1A - GA4 form_start`
- Tag `67`: `CEFA Phase 1A - GA4 form_submit_click`
- Tag `68`: `CEFA Phase 1A - GA4 validation_error`

The Google-side final tags remain active in public live GTM:

- Tag `35`: GA4 Google Tag `G-T65G018LYB`
- Tag `36`: GA4 `generate_lead` on `school_inquiry_submit`
- Tag `37`: Google Ads base tag `AW-802334988`
- Tag `38`: Google Ads conversion tag `AW-802334988/cFt-CMrLufgCEIzSyv4C`

## Tag Assistant Preview Result

The Tag Assistant file is a GTM `QUICK_PREVIEW`, not the currently published public container.

In preview, the plugin emitted one final parent event:

- Event: `school_inquiry_submit`
- Event ID: `14a9f951-1b2d-40ae-b09d-33ad40663129`
- Form ID: `4`
- Tracking source: `helper_plugin`
- Lead type: `cefa_lead`
- Lead intent: `inquire_now`
- School selected ID: `812370b7-bcad-11ef-8bcb-028d36469a89`
- School selected slug: `burnaby-kingsway`
- School selected name: `Burnaby - Kingsway`
- Program ID: `411`
- Program name: `CEFA Baby`
- Days per week: `2 days`
- Inquiry success URL included the one-time `cefa_tracking_token`

On the `school_inquiry_submit` event, Tag Assistant showed successful execution for:

- GA4 `generate_lead`
- Google Ads `Inquiry Submit_ollo`
- Meta Base Pixel
- Meta `Inquiry Submit`

The preview session showed consent granted for:

- `ad_storage`
- `analytics_storage`
- `ad_user_data`
- `ad_personalization`

## Interpretation

If Meta Base Pixel fired in preview but Meta `Inquiry Submit` was not visible in Meta Events Manager, the Tag Assistant export still shows Tag `40` executed successfully in preview.

Most likely explanations:

- The session was preview-only and not yet published to the live public container.
- Meta Events Manager/Test Events can lag or filter events even when `fbq()` executes.
- Public live GTM version `9` still has Tags `39` and `40` paused, so live visitors will not fire those Meta tags until a safe publish restores them.

Tag `40` executed in preview using:

- `fbq("trackCustom", "Inquiry Submit", payload, { eventID: event_id })`
- Pixel/dataset: `918227085392601`
- Event ID: `14a9f951-1b2d-40ae-b09d-33ad40663129`

## Required Guardrail

Do not reopen or publish these tags:

- Tag `66`: `CEFA Phase 1A - GA4 form_start`
- Tag `67`: `CEFA Phase 1A - GA4 form_submit_click`
- Tag `68`: `CEFA Phase 1A - GA4 validation_error`

Reason: these Custom HTML tags called `gtag()` for the same event name that triggered the GTM tag, which can self-trigger through `dataLayer` and destabilize pages.

## Safe Restore Plan

Next parent GTM publish should be narrowly scoped:

1. Keep tags `66`, `67`, and `68` paused.
2. Keep old POC/debug Custom HTML tags paused unless there is a specific preview-only reason.
3. Reopen only Tag `39` and Tag `40`.
4. Publish a named version such as `Restore parent Meta tags only - keep GA4 Custom HTML micro tags paused - 2026-05-05`.
5. Run one controlled Form 4 submission.
6. Confirm one `school_inquiry_submit`.
7. Confirm GA4 `generate_lead` fires.
8. Confirm Google Ads `AW-802334988/cFt-CMrLufgCEIzSyv4C` fires.
9. Confirm Meta Pixel PageView and Meta `Inquiry Submit` fire with the same event ID.
10. Confirm Contact Us dropdown no longer freezes and no repeated inline `G-T65G018LYB` scripts appear.

## Current Plan

Parent `cefa.ca` is close to intended Phase 1A state:

- Plugin source event works.
- Final payload values are clean.
- GA4 and Google Ads final tags remain live.
- Meta final tags work in preview but are not live until Tags `39` and `40` are published.

Do not move to cleanup or Phase 1B until the Meta-only restore publish is tested and the Contact Us/form stability regression is confirmed.
