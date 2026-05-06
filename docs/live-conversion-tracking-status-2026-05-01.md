# Live Conversion Tracking Status

Last updated: 2026-05-05

## Scope

This note records the current production-domain state after the parent live cutover and the first franchise live tracking bridge pass.

Checked properties:

- Parent Canada: `https://cefa.ca`
- Franchise Canada: `https://franchise.cefa.ca`
- Franchise USA: `https://franchisecefa.com`

## Executive Status

| Property | Website-side source | GTM/platform mapping | Status |
| --- | --- | --- | --- |
| `cefa.ca` | CEFA Conversion Tracking plugin | Active through `GTM-NZ6N7WNC` | Parent Phase 1A website/GTM path is working. |
| `franchise.cefa.ca` | WPCode fallback bridge + GAConnector selector map | Active through `GTM-TPJGHFS` Version `54` | Canada Phase 1 Form 1 continuity path maps to existing `Fr Application Submit` / `fr_application_submit`; post-v54 browser QA passed for Ads/GA4 and Meta script execution. |
| `franchisecefa.com` | WPCode fallback bridge | `GTM-5LZMHBZL` Version `15` GA4 helper-event mapping | Forms 1 and 2 push confirmed-success helper and dispatch events on the current live URLs. Form 2 has browser-level GA4 `generate_lead` evidence; processed GA4 reports, Form 1 GA4 receipt, and Ads/Meta final activation remain pending. |

## Parent Canada Current State

The parent live runtime is:

- Active GTM container: `GTM-NZ6N7WNC`
- Old parent GTM container: `GTM-PPV9ZRZ`, archived/reference-only
- WordPress source: `CEFA Conversion Tracking` plugin
- Tested live plugin version: `0.4.1`
- Repository plugin version after follow-up code changes: `0.4.2`
- Canonical parent event: `school_inquiry_submit`

Current parent result:

- One successful Form 4 submission creates one `school_inquiry_submit`.
- The browser `event_id` matches Gravity Forms field `32.4`.
- Field `32.3` days per week is not overwritten by the tracking plugin anymore.
- The saved multi-day value remains comma-separated for the business path.
- The dataLayer payload normalizes legacy pipe-delimited day values only for reporting.
- Attribution fields `35` through `46` are populated through the CEFA-owned attribution bridge.
- Direct thank-you visits and thank-you reloads do not push the final primary event.
- GTM maps the helper-plugin event to GA4/Google Ads/Meta.
- Live GA4 BigQuery export check for the last 7 days found `41` helper-plugin parent `generate_lead` events, `50` helper-plugin `validation_error` events, and no duplicate helper-plugin `generate_lead` event IDs.
- Current sampled live HTML loads `GTM-NZ6N7WNC` only; `GTM-PPV9ZRZ` is not present on the sampled live inquiry or thank-you pages.
- Legacy/non-helper `generate_lead` rows remain in the GA4 property from old thank-you URL patterns, but they lack `event_id`, `tracking_source`, and the helper-plugin metadata.

Guardrail:

- Do not reactivate the Gravity Forms Google Analytics Add-On as a second final conversion source.
- Do not map parent final conversions from the old `GTM-PPV9ZRZ` container.
- Do not use the School Manager business fields as tracking write targets beyond the approved `32.4` event ID field.

## Franchise Bridge Deployment

The franchise sites currently use a WPCode fallback bridge instead of the full plugin package because direct PHP plugin-file writes were blocked in the live hosting path.

Source file:

- `snippets/franchise-wpcode-bridge.php`

The fallback bridge:

- registers a one-time REST payload endpoint at `/wp-json/cefa-franchise-conversion/v1/payload/<event_id>`
- hooks Gravity Forms Form `1` and Form `2`
- stores the tracking `event_id` in Gravity Forms entry meta `cefa_conversion_tracking_event_id`
- appends `cefa_tracking=1` and `cefa_tracking_event_id=<uuid>` to successful confirmation URLs
- fetches the confirmed payload from the thank-you page with `POST` and `cache: no-store`
- consumes the server payload after one successful fetch
- pushes the final dataLayer event only after confirmed submission
- reads GAConnector fields `14` through `30` when present
- does not overwrite GAConnector, Synuma, SiteZeus, CRM delivery, notifications, or form UI behavior

Current public render check:

| URL | HTTP | GTM | Bridge markers |
| --- | --- | --- | --- |
| `https://franchise.cefa.ca/available-opportunities/franchising-inquiry/` | 200 | `GTM-TPJGHFS` | `cefa-franchise-conversion`, `franchise_inquiry_submit`, `POST`, `no-store`, `wpcode_bridge` |
| `https://franchise.cefa.ca/partner-with-cefa/real-estate-partners/submit-a-site/` | 200 | `GTM-TPJGHFS` | `cefa-franchise-conversion`, `real_estate_site_submit`, `POST`, `no-store`, `wpcode_bridge` |
| `https://franchisecefa.com/available-opportunities/franchising-inquiry/` | 200 | `GTM-5LZMHBZL` | `cefa-franchise-conversion`, `franchise_inquiry_submit`, `POST`, `no-store`, `wpcode_bridge` |
| `https://franchisecefa.com/partner-with-cefa/real-estate-partners/submit-a-site/` | 200 | `GTM-5LZMHBZL` | `cefa-franchise-conversion`, `real_estate_site_submit`, `POST`, `no-store`, `wpcode_bridge` |

## Franchise Canada Evidence

Runtime:

- Domain: `franchise.cefa.ca`
- GTM: `GTM-TPJGHFS`
- Published GTM version: `54` / `CEFA Franchise Canada legacy thank-you duplicate guard - 2026-05-05`
- GA4 property: `259747921` / `CEFA Franchise`
- Linked Google Ads customer: `3820636025`
- Meta pixel/dataset kept on the existing shared franchise pixel: `918227085392601`
- LinkedIn partner ID kept as `4536524`

GTM implementation:

- Raw helper events remain `franchise_inquiry_submit` and `real_estate_site_submit`.
- GTM adds a short delayed dispatch event before firing platform tags:
  - `cefa_franchise_inquiry_dispatch`
  - `cefa_real_estate_site_dispatch`
- The dispatch layer prevents lost destination hits when the confirmed helper event arrives before destination libraries are fully ready.
- Existing destination IDs were preserved instead of creating new platform learning surfaces.
- GAConnector tag `GA Connector - CRM` was updated to map GAConnector cookie values into Gravity Forms hidden fields `14` through `30` for Form `1` and Form `2`.
- 2026-05-05 correction: Form `1` helper submit now maps to Google Ads primary `fr_application_submit` (`AW-11088792613/cys-CIHslY4YEKWYxqcp`) and Meta `Fr Application Submit` on dataset `918227085392601`, because live ad sets/custom conversions optimize against `Fr Application Submit` rather than `Fr Inquiry Submit`.
- 2026-05-05 duplicate guard: legacy `/thank-you` pageview trigger `38` was disabled and legacy Meta pageview tag `51` was paused.

Form 1 / Franchise Inquiry:

- Final website event: `franchise_inquiry_submit`
- Dispatch event for destination tags: `cefa_franchise_inquiry_dispatch`
- Latest validated event ID: `77b52ed9-2ffe-42ef-b98a-293c27ed4d13`
- Event ID storage: Gravity Forms entry meta `cefa_conversion_tracking_event_id`
- Payload context: `site_context=franchise_ca`, `market=canada`, `country=CA`, `form_id=1`, `form_family=franchise_inquiry`, `lead_type=franchise_lead`
- Confirmed non-PII lead metadata included location interest/name, investment range, opening timeline, school count goal, and ownership structure.
- Confirmed attribution fields saved/pushed cleanly: `lc_source`, `lc_medium`, `lc_campaign`, `lc_content`, `lc_term`, `lc_channel`, `lc_landing`, `lc_referrer`, `fc_source`, `fc_medium`, `fc_campaign`, `fc_content`, `fc_term`, `fc_channel`, `fc_referrer`, `gclid`, and `ga_client_id`.
- Confirmed GA4/Google measurement hit for `generate_lead`.
- Historical controlled test before the 2026-05-05 continuity correction confirmed Google Ads conversion hit for conversion ID `11088792613`, label `MfYYCITslY4YEKWYxqcp`; this secondary `fr_inquiry_submit` tag is now paused.
- Historical controlled test before the 2026-05-05 continuity correction confirmed Meta custom event `Fr Inquiry Submit` on pixel `918227085392601` with matching `event_id`; Form `1` now maps to `Fr Application Submit` for platform-learning continuity.
- Confirmed LinkedIn conversion ID `11308340` with matching `event_id`.
- Direct payload request after browser consumption returned `404`.
- Thank-you reload did not push another final event.
- Post-Version-54 controlled Form `1` browser QA verified event ID `ad5901f8-0dbb-4281-97cc-88dd0c2d86d3`, one `franchise_inquiry_submit`, one `cefa_franchise_inquiry_dispatch`, Google Ads primary label `cys-CIHslY4YEKWYxqcp`, GA4 `generate_lead`, no secondary Ads label `MfYYCITslY4YEKWYxqcp`, and Meta `Fr Application Submit` script execution.
- Meta Events Manager receipt and delayed GA4/Google Ads processed reporting confirmation remain pending.

Form 2 / Submit a Site:

- Final website event: `real_estate_site_submit`
- Dispatch event for destination tags: `cefa_real_estate_site_dispatch`
- Latest validated event ID: `5462203a-7857-4de0-93b9-fa83a5b61b94`
- Event ID storage: Gravity Forms entry meta `cefa_conversion_tracking_event_id`
- Payload context: `site_context=franchise_ca`, `market=canada`, `country=CA`, `form_id=2`, `form_family=site_inquiry`, `lead_type=real_estate_lead`
- Confirmed non-PII site metadata included site offered by, square-footage range, outdoor-space range, and availability timeline.
- Confirmed GA4 `generate_lead` hit with site-submission metadata.
- Confirmed Google Ads conversion hits for conversion ID `11088792613`, label `vq7GCIrslY4YEKWYxqcp`, and conversion ID `802334988`, label `lZGsCLenuvgCEIzSyv4C`.
- Confirmed Meta custom event `Fr Site Form Submit` on pixel `918227085392601` with matching `event_id`.
- Confirmed LinkedIn conversion ID `11308348` with matching `event_id`.
- Direct payload request after browser consumption returned `404`.

## Franchise USA Evidence

Runtime:

- Domain: `franchisecefa.com`
- GTM: `GTM-5LZMHBZL`
- Published GTM version: `15` / `CEFA Franchise USA Phase 1 helper-event GA4 mapping - 2026-05-01`
- GA4 property: `519783092` / `CEFA Franchise - USA.`
- Linked Google Ads customers: `3820636025`, `4159217891`
- GA4 currency currently: `CAD`

Current production form URLs:

- Form `1` / Franchise Inquiry: `https://franchisecefa.com/available-opportunities/franchising-inquiry/`
- Form `2` / Submit a Site: `https://franchisecefa.com/partner-with-cefa/real-estate-partners/submit-a-site/`

URL correction from 2026-05-03:

- `https://franchisecefa.com/franchise-application/` now returns `404`.
- `https://franchisecefa.com/real-estate-submission/` now returns `404`.
- Use the current URLs above for launch QA and ad landing-page checks.

Form 1 / Franchise Inquiry:

- Final event: `franchise_inquiry_submit`
- Latest post-Version-15 test event ID: `4adf41e8-0f00-4051-acb5-0ad780fe84f1`
- Event ID storage: Gravity Forms entry meta `cefa_conversion_tracking_event_id`
- Payload context: `site_context=franchise_us`, `market=usa`, `country=US`, `form_id=1`, `form_family=franchise_inquiry`, `lead_type=franchise_lead`
- Confirmed dispatch event: `cefa_franchise_us_inquiry_dispatch`
- Confirmed non-PII lead metadata included `location_interest=1190`, investment range, opening timeline, school count goal, and ownership structure.
- The submitted `location_interest` value was the Gravity Forms value `1190`, not the visible location label.
- Browser dataLayer/helper evidence is confirmed. GA4 browser-hit or processed-report evidence for Form 1 remains pending.

Form 2 / Submit a Site:

- Final event: `real_estate_site_submit`
- Latest post-Version-15 test event ID: `75716e51-70bd-4023-be4e-eec4f32ea468`
- Event ID storage: Gravity Forms entry meta `cefa_conversion_tracking_event_id`
- Payload context: `site_context=franchise_us`, `market=usa`, `country=US`, `form_id=2`, `form_family=site_inquiry`, `lead_type=real_estate_lead`
- Confirmed dispatch event: `cefa_franchise_us_site_dispatch`
- Confirmed non-PII site metadata included site offered by, square-footage range, outdoor-space range, and availability timeline.
- Browser resource evidence confirmed a GA4 `generate_lead` request to `G-YL1KQPWV0M` with matching event ID, helper metadata, `value=250`, and `currency=USD`.
- Base Google tag and remarketing/config requests for `AW-11088792613` were present, but this is not proof that a final Google Ads lead conversion is active.

GTM Version 15 implementation:

- The live USA container now contains hostname/context-scoped helper triggers for `franchise_inquiry_submit` and `real_estate_site_submit`.
- The helper triggers require `Page Hostname` to match `franchisecefa.com` or `www.franchisecefa.com`, `site_context=franchise_us`, and `market=usa`.
- GTM creates delayed dispatch events before destination firing:
  - `cefa_franchise_us_inquiry_dispatch`
  - `cefa_franchise_us_site_dispatch`
- Active destination mapping added:
  - `CEFA - GA4 - Franchise USA - generate_lead - inquiry`
  - `CEFA - GA4 - Franchise USA - generate_lead - site`
- The active GA4 mapping sends only non-PII helper payload fields to `G-YL1KQPWV0M`.
- Legacy USA final conversion tags from the old Elementor/form-submit path were paused to avoid duplicate final conversions:
  - `Franchisor_GA4_Fr Application Submit_ollo`
  - `Franchisor_GA4_Fr Site Form Submit_ollo`
  - `Franchisor_GAds_Fr Application Submit_ollo`
  - `Franchisor_GAds_Fr Site Form Submit_ollo`
  - `Franchisor_FB_Fr Application Submit_ollo`
  - `Franchisor_FB_Site Form Submit_ollo`
  - `cHTML - Fr Apply Success Listener (USA)_ollo`
- USA Google Ads and Meta final helper-event tags were not activated because USA-specific conversion action labels and Meta dataset/pixel ownership are not yet verified.
- Live `gtm.js` render check confirms the published container includes `franchise_inquiry_submit`, `real_estate_site_submit`, `cefa_franchise_us_inquiry_dispatch`, `cefa_franchise_us_site_dispatch`, and `G-YL1KQPWV0M`.
- 2026-05-03 live `gtm.js` check still confirms the same helper, dispatch, and GA4 markers.

## GA4 Admin Status

Parent `267558140`:

- Phase 1A event-scoped custom dimensions for the parent helper-plugin payload are registered.
- `generate_lead` already exists as a key event.
- `validation_error` is not a GA4 key event.
- The property is linked to Google Ads customer `4159217891`.

Franchise Canada `259747921`:

- Property exists and is linked to Google Ads customer `3820636025`.
- Existing legacy/reporting dimensions remain in place, including `event_title`, `event_label`, `preferred_location`, `applicant_capital`, page/click fields, and video fields.
- The low-cardinality helper-plugin franchise parameters are now registered as event-scoped custom dimensions: `site_context`, `business_unit`, `market`, `country`, `form_id`, `form_family`, `lead_type`, `lead_intent`, `tracking_source`, `event_scope`, `server_transport`, `location_interest`, `investment_range`, `opening_timeline`, `school_count_goal`, `ownership_structure`, `site_offered_by`, `property_square_footage_range`, `outdoor_space_range`, `availability_timeline`, `lc_channel`, and `fc_channel`.
- GA4 Data API processing check for `2026-04-30` through `2026-05-01` returned one processed `generate_lead` row on host `franchise.cefa.ca`.
- GA4 Data API processing refresh for `2026-05-01` through `2026-05-03` returned `4` processed `generate_lead` rows on host `franchise.cefa.ca`: `1` row with helper metadata `site_context=franchise_ca`, `form_family=franchise_inquiry`, `lead_type=franchise_lead`, and `tracking_source=helper_plugin`, plus `3` older/not-set rows.
- A same-day `2026-05-01` report and realtime check returned no active `generate_lead` rows at the time of verification.
- High-cardinality values such as `event_id`, click IDs, full URLs, landing URLs, referrers, GA client IDs, and Gravity Forms entry IDs were intentionally not registered as GA4 custom dimensions.

Franchise USA `519783092`:

- Property exists and is linked to Google Ads customers `3820636025` and `4159217891`.
- The same low-cardinality franchise helper parameters listed above are now registered as event-scoped custom dimensions.
- Currency is currently `CAD`; confirm whether that should remain or change before production reporting signoff.
- GA4 Data API checks for `2026-05-01` through `2026-05-03`, filtered to `eventName=generate_lead`, returned no processed USA rows at the time of the 2026-05-03 check.
- Realtime API checks for `generate_lead`, helper events, and dispatch events also returned no rows at the time of the 2026-05-03 check.
- Browser-resource evidence still confirms Form `2` sent `generate_lead` to `G-YL1KQPWV0M`; processed reporting should be rechecked after the GA4 delay.

## Google Ads Admin Status

Supermetrics reporting access confirmed Google Ads account `3820636025` / `CEFA Franchisor`.

2026-05-03 refresh:

- Google Ads source `AW` is authenticated in Supermetrics for `mert.atalay@cefa.ca`.
- Connected Google Ads accounts visible for franchise/USA checks: `3820636025` / `CEFA Franchisor` and `4159217891` / `CEFA $3000`.
- The Supermetrics campaign/resource conversion endpoint returned an OAuth-token limitation, but the standard Google Ads reporting query worked for conversion-action reporting.
- This is reporting evidence only. Direct Google Ads admin edits still require a proper Google Ads API setup and explicit media-owner approval before changing primary/secondary status.

Conversion action primary/secondary review for `2025-05-01` through `2026-05-01`:

| Conversion action | Tracker ID | Category | Primary for goal | All conversions |
| --- | --- | --- | --- | --- |
| `fr_application_submit` | `6472168961` | Submit lead form | `true` | `96` |
| `generate_lead (GA4)` | `6480960234` | Submit lead form | `false` | `82.51` |
| `fr_site_form_submit` | `6472168970` | Submit lead form | `false` | `3` |
| `fr_inquiry_submit` | `6472168964` | Submit lead form | `false` | `0` |
| `Application Submit (USA)` | `7482298930` | Submit lead form | `true` | `0` |
| `CEFA Franchise - USA. (web) generate_lead` | `7499744287` | Submit lead form | `false` | `0` |
| `CEFA Franchise - USA. (web) ads_conversion_submit_lead_form` | `7482257746` | Submit lead form | `false` | `0` |

2026-05-03 USA-linked account refresh for `2025-05-01` through `2026-05-03`:

| Account | Conversion action | Tracker ID | Category | Primary for goal | All conversions |
| --- | --- | --- | --- | --- | --- |
| `3820636025` | `Application Submit (USA)` | `7482298930` | Submit lead form | `true` | `0` |
| `3820636025` | `CEFA Franchise - USA. (web) generate_lead` | `7499744287` | Submit lead form | `false` | `0` |
| `3820636025` | `CEFA Franchise - USA. (web) ads_conversion_submit_lead_form` | `7482257746` | Submit lead form | `false` | `0` |
| `4159217891` | `CEFA Franchise - USA. (web) generate_lead` | `7499970414` | Submit lead form | `false` | `0` |
| `4159217891` | `Cefafranchise.com | Request Info Submission` | `293368274` | Submit lead form | `false` | `0` |

Interpretation:

- Canada browser evidence confirms Ads tags fired, but the relevant `fr_inquiry_submit`, `fr_site_form_submit`, and imported GA4 `generate_lead` conversion actions are secondary at the time of verification.
- `fr_application_submit` is primary and has historical volume, but it is not the same as the new Form 1 helper event name.
- Do not change bidding/primary settings from this repository evidence alone. Before any live Ads setting edit, confirm the intended bidding action with the media owner and Ads UI/API, then document the exact old to new change.
- USA Ads final helper-event mapping is still not activated because the correct USA account and bidding action have not been approved. The linked/imported USA GA4 actions exist, but they have zero reporting volume in the checked period and should not be treated as proven bidding signals yet.

## Meta Admin Status

- Canada browser/network evidence confirms Meta received `Fr Inquiry Submit` and `Fr Site Form Submit` on pixel/dataset `918227085392601` with matching event IDs during controlled tests.
- Meta Events Manager UI/API custom-conversion status was not verified in this pass. Supermetrics reporting/account discovery does not expose Events Manager custom conversion definitions through the available endpoint.
- Franchise Canada custom conversions inside the current shared dataset remain pending until Events Manager is checked directly.
- Franchise USA final Meta tags remain blocked. The live USA container still has the existing shared-pixel base pageview tag, but final USA lead/site-submit events were not newly mapped to the shared dataset because USA should stay separated unless a live campaign dependency is explicitly confirmed.

## What Is Still Pending

Franchise Canada Phase 1 browser/platform mapping is now working from live browser evidence. Remaining items are admin/reporting cleanup, explicit Meta custom-conversion confirmation, and Google Ads primary/secondary decisioning. Franchise USA now has live website helper events, dispatch events, and GA4 mapping, but processed GA4 reporting, Form 1 GA4 receipt, and Ads/Meta final mappings remain blocked or pending.

Pending work:

- Evaluate GA4 Measurement Protocol as a Phase 1B audit-only server-side event, not as a duplicate `generate_lead` source.
- Confirm Form 1 and Form 2 helper-event parameters in GA4 reports after custom dimensions are registered and processing completes.
- Decide whether current Google Ads primary/secondary settings are correct for Canada reporting and bidding. Do not change primary status without explicit media-owner approval.
- Confirm Meta Events Manager receives the Canada events and create/adjust franchise-specific custom conversions inside the current shared dataset.
- Recheck USA GA4 processed reports after the 2026-05-03 controlled submissions.
- Confirm USA Form 1 GA4 `generate_lead` browser hit or processed report row.
- Confirm the intended USA Google Ads account and primary/bidding conversion action before activating Ads final helper-event tags.
- Confirm USA Meta dataset/pixel before activating Meta final helper-event tags.
- Monitor GTM cache propagation; clean Canada contexts loaded Version `52`, and clean USA contexts load Version `15`.

## Current Interpretation

Parent Canada is complete enough to keep live and monitor.

Franchise Canada is now Phase 1 browser/platform functional: confirmed-success website events, attribution writeback, dispatch-layer GTM mapping, live destination hits, one processed GA4 `generate_lead` report row, and GA4 custom-dimension registration are verified. It still needs Meta custom-conversion confirmation and a Google Ads primary/secondary decision before reporting signoff.

Franchise USA now has the confirmed-success website-side dataLayer source, a live GTM Version `15` GA4 helper-event mapping, GA4 custom-dimension registration, and post-Version-15 controlled submissions for both current live forms. Form 2 has browser-level GA4 `generate_lead` evidence. Ads/Meta final mapping remains intentionally blocked pending USA-specific platform confirmation, and processed GA4 reporting plus Form 1 GA4 receipt still need follow-up.

Measurement Protocol remains a Phase 1B strengthening layer. If tested through the Gravity Forms Google Analytics Add-On, it should first send an audit-only event such as `franchise_us_inquiry_submit_server_audit` with the same `event_id`, not a second GA4 `generate_lead`. USA Form 1 `location_interest` must be sent with the lowercase parameter name `location_interest` and the submitted answer value, not the literal field question.
