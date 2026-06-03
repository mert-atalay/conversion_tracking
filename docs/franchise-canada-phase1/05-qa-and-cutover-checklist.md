# Franchise Canada QA And Cutover Checklist

Last updated: 2026-05-05

Status note: this checklist reflects the live-domain Version 52 GTM pass on `franchise.cefa.ca`, the 2026-05-04 GAConnector cleanup patch, and the 2026-05-05 Version 54 continuity correction. Controlled live Form 1 and Form 2 submissions on 2026-05-04 both reached their thank-you pages, pushed the expected helper events, created Gravity Forms entries, saved matching `cefa_conversion_tracking_event_id` values, and appeared in GA4 realtime as `generate_lead`. The later Form 2 retest verified the stale same-session `gclid` issue is fixed by preferring the current Google `_gcl_aw` value before Gravity Forms saves the entry. The post-Version-54 Form 1 browser QA on 2026-05-05 verified Google Ads primary `fr_application_submit`, GA4 `generate_lead`, no secondary Ads `fr_inquiry_submit`, and Meta `Fr Application Submit` script execution.

Continuity correction on 2026-05-05:

- Live GTM Version `54` changed the Form `1` helper-submit destination from the secondary `fr_inquiry_submit` path to the existing primary/optimized `fr_application_submit` path.
- The neutral website event remains `franchise_inquiry_submit`.
- Meta helper tag `52` now sends `Fr Application Submit` with the helper `event_id`, preserving the currently optimized `Fr Application Submit_CAD` custom conversion path on dataset `918227085392601`.
- Google Ads tag `27` now fires from trigger `197` with label `AW-11088792613/cys-CIHslY4YEKWYxqcp`.
- Google Ads tag `28` / `fr_inquiry_submit` is paused to avoid duplicate final Ads hits.
- Legacy pageview trigger `38` is disabled by matching only `__cefa_disabled_legacy_thank_you_application_submit__`; old pageview Meta tag `51` is paused.
- Post-Version-54 controlled Form `1` browser QA is recorded in [08-post-v54-application-submit-qa-2026-05-05.md](./08-post-v54-application-submit-qa-2026-05-05.md). Platform UI/reporting confirmation remains pending for Meta Events Manager and delayed GA4/Google Ads processed reports.

Admin/reporting recheck on 2026-05-01:

- GA4 property `259747921` is visible and linked to Google Ads customer `3820636025`.
- GA4 Data API reported one processed `generate_lead` on host `franchise.cefa.ca` for `2026-04-30` through `2026-05-01`.
- Same-day `2026-05-01` and realtime GA4 checks were empty at verification time, so the processed report is evidence of receipt but not a complete same-day Form 1/Form 2 reporting split.
- GA4 custom dimensions for the low-cardinality helper payload were registered through the GA4 Admin API after ADC was refreshed with Analytics edit scope.
- Google Ads conversion-action review found `fr_application_submit` primary, while `fr_inquiry_submit`, `fr_site_form_submit`, and imported `generate_lead (GA4)` are secondary.
- Meta browser/network receipt is verified from controlled tests, but Events Manager custom conversion setup was not API/UI verified in this pass.

Admin/reporting refresh on 2026-05-03:

- Fresh `gtm.js` check for `GTM-TPJGHFS` still contains `franchise_inquiry_submit`, `real_estate_site_submit`, `cefa_franchise_inquiry_dispatch`, and `cefa_real_estate_site_dispatch`.
- GA4 Data API for `2026-05-01` through `2026-05-03` reported `4` processed `generate_lead` rows on host `franchise.cefa.ca`: `1` row with helper metadata `site_context=franchise_ca`, `form_family=franchise_inquiry`, `lead_type=franchise_lead`, `tracking_source=helper_plugin`, plus `3` older/not-set rows.
- GA4 property `259747921` remains linked to Google Ads customer `3820636025`.
- Google Ads reporting-query evidence through Supermetrics still shows `fr_application_submit` as primary and `generate_lead (GA4)`, `fr_site_form_submit`, and `fr_inquiry_submit` as secondary in account `3820636025`.
- Direct Meta Events Manager custom-conversion setup was still not available through the current tool access; it remains a UI/API confirmation item.

Live main-conversion refresh on 2026-05-04:

- Form 1 controlled submission emitted `franchise_inquiry_submit` with event ID `bbf3bbef-2154-48d9-b036-8f54e4bee3e3`; Gravity Forms entry `44` saved the same event ID and a `cefa_synuma_lead_id`.
- Form 2 controlled submission emitted `real_estate_site_submit` with event ID `740e7413-9cbc-4410-a19f-53a5e0e34e80`; Gravity Forms entry `45` saved the same event ID and a `cefa_synuma_lead_id`.
- GA4 realtime for property `259747921` showed `2` `generate_lead` events after the Form 1 and Form 2 tests.
- Initial Form 2 saved GAConnector fields `14`, `15`, `16`, `29`, and `30`, but field `29` used the earlier Form 1 `gclid`; this triggered the cleanup patch.
- Post-patch Form 2 retest saved Gravity Forms entry `46` with `14=qa_tracking`, `15=live_patch`, `16=gaconnector_backfill_20260504`, `29=QA-FRCA-PATCH-SITE-20260504`, and `30=1065795917.1777927212`; the dataLayer `real_estate_site_submit` payload carried the same current click ID and clean separate attribution parameters.

## Before GTM Build

- [x] Confirm GTM account/container for Canada franchise.
- [x] Confirm new staging currently loads `GTM-TPJGHFS`.
- [x] Confirm GA4 property `259747921` is visible through GA4 Admin MCP.
- [x] Confirm Form 1 / Franchise Inquiry exists on staging.
- [x] Confirm Form 2 / Site Inquiry exists on staging.
- [x] Confirm Form 3 / Newsletter exists on staging.
- [x] Confirm Form 1 confirmation page.
- [x] Confirm Form 2 confirmation page.
- [x] Confirm existing attribution hidden fields `14` through `30`.
- [x] Confirm GAConnector scripts/cookies load on staging runtime.
- [x] Confirm `gclid` can populate hidden field `29` in runtime tests.
- [x] Confirm real Form 1 entry/runtime saves clean fields `14` through `30`.
- [x] Confirm real Form 2 entry saves clean/current fields `14` through `30` after the GAConnector cleanup patch.
- [x] Confirm whether GAConnector populates `lc_*`, `fc_*`, and `GA_Client_ID` reliably after real submissions.
- [x] Decide whether helper plugin should backfill missing attribution values if GAConnector fields remain empty.
- [x] Confirm Meta dataset decision for Canada transition.
- [x] Confirm Google Ads conversion action labels.
- [x] Confirm whether staging should keep `GTM-TPJGHFS` or switch to a clean staging container.

## Helper Plugin QA

- [x] Plugin code supports Franchise Canada hostnames `cefafranchise.kinsta.cloud` and `franchise.cefa.ca`.
- [x] Plugin code supports Form `1` and Form `2` confirmed-success payload contracts.
- [x] Plugin code reads GAConnector fields `14` through `30`, backfills missing/placeholder values from GAConnector cookies, and overwrites stale `gclid` only when the current Google `_gcl_aw` cookie proves a newer click ID.
- [x] Deploy temporary WPCode fallback bridge on live Franchise Canada.
- [x] Form 1 success emits exactly one `franchise_inquiry_submit`.
- [x] Form 2 success emits exactly one `real_estate_site_submit`.
- [x] Form 1 event has `site_context: franchise_ca`.
- [x] Form 2 event has `site_context: franchise_ca`.
- [x] Form 1 event has `event_id`.
- [x] Form 2 event has `event_id`.
- [x] Event IDs are unique per successful submission.
- [x] Event IDs are available in Gravity Forms entry meta.
- [x] Existing GAConnector attribution values are preserved when populated.
- [x] Empty attribution fields are not silently treated as verified tracking success.
- [x] Direct Form 1 thank-you page visit fires no primary event.
- [x] Direct Form 2 thank-you page visit fires no primary event.
- [x] Thank-you page reload fires no duplicate event.
- [ ] Invalid Form 1 submission fires no primary event.
- [ ] Invalid Form 2 submission fires no primary event.
- [x] No PII is pushed into the helper-event dataLayer payload.

## GTM QA

- [ ] GTM preview shows primary Form 1 event only after confirmed success.
- [ ] GTM preview shows primary Form 2 event only after confirmed success.
- [ ] Staging tags are hostname-contained to `cefafranchise.kinsta.cloud`.
- [x] Live host `franchise.cefa.ca` renders the intended bridge markers after deployment.
- [x] GA4 receives expected event and parameters from browser/network evidence.
- [x] Google Ads tags are enabled only after conversion labels were confirmed/reused.
- [x] Meta tags are enabled only after the Canada shared-dataset transition decision was confirmed.
- [ ] Micro-conversions are not marked as Google Ads bidding conversions.

## Production Cutover

- [x] Replace staging hostname conditions with production hostname conditions.
- [x] Verify production `franchise.cefa.ca` loads the intended GTM container.
- [x] Submit Form 1 in production test mode and verify one primary event.
- [x] Submit Form 2 in production test mode and verify one primary event.
- [ ] Confirm CRM/Synuma/SiteZeus delivery still works.
- [x] Confirm GA4 realtime receives events after controlled live Form 1/Form 2 submissions.
- [x] Confirm processed GA4 Data API event reporting includes `generate_lead` on `franchise.cefa.ca`.
- [x] Confirm GA4 custom dimensions are registered for low-cardinality helper payload reporting fields.
- [x] Confirm Google Ads primary/secondary status through reporting API evidence.
- [x] Confirm Google Ads only receives approved final conversion events from browser/network evidence.
- [x] Confirm Meta only receives approved final conversion events from browser/network evidence.
- [ ] Confirm custom conversions separate franchise Canada from parent and USA.
- [x] Preserve Google Ads bidding continuity by mapping Form `1` helper submit to existing primary `fr_application_submit`.
- [x] Preserve Meta campaign continuity by mapping Form `1` helper submit to existing `Fr Application Submit` custom event.
- [x] Disable legacy `/thank-you` pageview application-submit trigger so old pageview tags cannot duplicate the helper submit.
- [x] Run post-Version-54 Form `1` controlled browser submission and confirm one Google Ads `fr_application_submit`, one GA4 `generate_lead`, Meta `Fr Application Submit` script execution, and no secondary `fr_inquiry_submit` Ads hit.
- [ ] Confirm post-Version-54 `Fr Application Submit` receipt in Meta Events Manager UI after platform processing delay.
- [ ] Confirm post-Version-54 GA4 and Google Ads processed reporting rows after platform processing delay.
