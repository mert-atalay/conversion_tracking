# Franchise Canada QA And Cutover Checklist

Last updated: 2026-05-01

Status note: this checklist reflects the live-domain Version 52 GTM pass on `franchise.cefa.ca`. GAConnector field population is verified on a clean Form 1 runtime test; Form 2 uses the same selector map and final destination mapping is verified, but a final post-Version-52 Form 2 attribution re-submit can still be run if stricter evidence is needed.

Admin/reporting recheck on 2026-05-01:

- GA4 property `259747921` is visible and linked to Google Ads customer `3820636025`.
- GA4 Data API reported one processed `generate_lead` on host `franchise.cefa.ca` for `2026-04-30` through `2026-05-01`.
- Same-day `2026-05-01` and realtime GA4 checks were empty at verification time, so the processed report is evidence of receipt but not a complete same-day Form 1/Form 2 reporting split.
- GA4 custom dimensions for the new helper payload are still not registered. Direct Admin API creation was blocked by the local ADC token scope.
- Google Ads conversion-action review found `fr_application_submit` primary, while `fr_inquiry_submit`, `fr_site_form_submit`, and imported `generate_lead (GA4)` are secondary.
- Meta browser/network receipt is verified from controlled tests, but Events Manager custom conversion setup was not API/UI verified in this pass.

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
- [ ] Confirm real Form 2 entry saves clean fields `14` through `30` after Version 52.
- [x] Confirm whether GAConnector populates `lc_*`, `fc_*`, and `GA_Client_ID` reliably after real submissions.
- [x] Decide whether helper plugin should backfill missing attribution values if GAConnector fields remain empty.
- [x] Confirm Meta dataset decision for Canada transition.
- [x] Confirm Google Ads conversion action labels.
- [x] Confirm whether staging should keep `GTM-TPJGHFS` or switch to a clean staging container.

## Helper Plugin QA

- [x] Plugin code supports Franchise Canada hostnames `cefafranchise.kinsta.cloud` and `franchise.cefa.ca`.
- [x] Plugin code supports Form `1` and Form `2` confirmed-success payload contracts.
- [x] Plugin code reads GAConnector fields `14` through `30` and does not overwrite them.
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
- [ ] Confirm GA4 realtime/debug view receives events in platform UI after processing delay.
- [x] Confirm processed GA4 Data API event reporting includes `generate_lead` on `franchise.cefa.ca`.
- [x] Confirm Google Ads primary/secondary status through reporting API evidence.
- [x] Confirm Google Ads only receives approved final conversion events from browser/network evidence.
- [x] Confirm Meta only receives approved final conversion events from browser/network evidence.
- [ ] Confirm custom conversions separate franchise Canada from parent and USA.
