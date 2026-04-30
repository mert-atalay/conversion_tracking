# Franchise Canada QA And Cutover Checklist

Last updated: 2026-04-30

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
- [ ] Confirm real Form 1 entry saves clean fields `14` through `30`.
- [ ] Confirm real Form 2 entry saves clean fields `14` through `30`.
- [ ] Confirm whether GAConnector populates `lc_*`, `fc_*`, and `GA_Client_ID` reliably after real submissions.
- [ ] Decide whether helper plugin should backfill missing attribution values if GAConnector fields remain empty.
- [ ] Confirm Meta dataset decision for Canada transition.
- [ ] Confirm Google Ads conversion action labels.
- [ ] Confirm whether staging should keep `GTM-TPJGHFS` or switch to a clean staging container.

## Helper Plugin QA

- [x] Plugin code supports Franchise Canada hostnames `cefafranchise.kinsta.cloud` and `franchise.cefa.ca`.
- [x] Plugin code supports Form `1` and Form `2` confirmed-success payload contracts.
- [x] Plugin code reads GAConnector fields `14` through `30` and does not overwrite them.
- [ ] Upload and activate plugin version `0.4.0` on Franchise Canada staging.
- [ ] Form 1 success emits exactly one `franchise_inquiry_submit`.
- [ ] Form 2 success emits exactly one `real_estate_site_submit`.
- [ ] Form 1 event has `site_context: franchise_ca`.
- [ ] Form 2 event has `site_context: franchise_ca`.
- [ ] Form 1 event has `event_id`.
- [ ] Form 2 event has `event_id`.
- [ ] Event IDs are unique per successful submission.
- [ ] Event IDs are available in Gravity Forms entry meta.
- [ ] Existing GAConnector attribution values are preserved when populated.
- [ ] Empty attribution fields are not silently treated as verified tracking success.
- [ ] Direct Form 1 thank-you page visit fires no primary event.
- [ ] Direct Form 2 thank-you page visit fires no primary event.
- [ ] Thank-you page reload fires no duplicate event.
- [ ] Invalid Form 1 submission fires no primary event.
- [ ] Invalid Form 2 submission fires no primary event.
- [ ] No PII is pushed into dataLayer.

## GTM QA

- [ ] GTM preview shows primary Form 1 event only after confirmed success.
- [ ] GTM preview shows primary Form 2 event only after confirmed success.
- [ ] Staging tags are hostname-contained to `cefafranchise.kinsta.cloud`.
- [ ] Old live host `franchise.cefa.ca` is unaffected during staging tests.
- [ ] GA4 receives expected event and parameters.
- [ ] Google Ads tags are not enabled until conversion labels are confirmed.
- [ ] Meta tags are not enabled until dataset transition decision is confirmed.
- [ ] Micro-conversions are not marked as Google Ads bidding conversions.

## Production Cutover

- [ ] Replace staging hostname conditions with production hostname conditions.
- [ ] Verify production `franchise.cefa.ca` loads the intended GTM container.
- [ ] Submit Form 1 in production test mode and verify one primary event.
- [ ] Submit Form 2 in production test mode and verify one primary event.
- [ ] Confirm CRM/Synuma/SiteZeus delivery still works.
- [ ] Confirm GA4 realtime/debug view receives events.
- [ ] Confirm Google Ads only receives approved final conversion events.
- [ ] Confirm Meta only receives approved final conversion events.
- [ ] Confirm custom conversions separate franchise Canada from parent and USA.
