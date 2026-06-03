# Franchise USA QA And Cutover Checklist

Last updated: 2026-05-06

Status note: controlled live submissions were re-run on 2026-05-04 using the current production URLs. Form `1` and Form `2` both reached thank-you pages, pushed the expected helper and dispatch events, sent GA4 `generate_lead` hits to `G-YL1KQPWV0M`, appeared in GA4 realtime, and created Gravity Forms entries with matching `cefa_conversion_tracking_event_id` values. Main conversion event signoff is pass. The later GAConnector cleanup patch fixed the blank helper-payload attribution issue for both USA forms. GTM Version `16` moved USA Meta to dataset `1531247935333023`; GTM Version `17` then paused remaining active legacy micro/click tags; GTM Version `18` added a Meta `fbq` init fallback; GTM Version `19` added the USA attribution hidden-field writer for Form `1` and Form `2`. The remaining issue is the active Gravity Forms Google Analytics Form `1` feed.

Live main-conversion refresh on 2026-05-04:

- Form 1 controlled submission emitted `franchise_inquiry_submit` and `cefa_franchise_us_inquiry_dispatch` with event ID `cd1297db-30a6-46ab-b22a-169f01230878`; Gravity Forms entry `34` saved the same event ID and a `cefa_synuma_lead_id`.
- Form 2 controlled submission emitted `real_estate_site_submit` and `cefa_franchise_us_site_dispatch` with event ID `c6492cf5-655e-4af0-abef-c6af792eff66`; Gravity Forms entry `35` saved the same event ID and a `cefa_synuma_lead_id`.
- GA4 realtime for property `519783092` showed `2` `generate_lead` events after the Form 1 and Form 2 tests.
- Initial clean isolated browser testing showed GAConnector cookies populated, but helper dataLayer attribution values were blank; this triggered the cleanup patch.
- Post-patch Form 1 retest saved Gravity Forms entry `37` with `14=qa_tracking`, `15=live_patch`, `16=gaconnector_backfill_20260504`, `29=QA-FRUS-PATCH-INQ-20260504`, and `30=1930300797.1777927657`; the `franchise_inquiry_submit` payload carried the same clean attribution values.
- Post-patch Form 2 retest saved Gravity Forms entry `36` with `14=qa_tracking`, `15=live_patch`, `16=gaconnector_backfill_20260504`, `29=QA-FRUS-PATCH-SITE-20260504`, and `30=1618510533.1777927481`; the `real_estate_site_submit` payload carried the same clean attribution values.
- WordPress still has Gravity Forms Google Analytics active with an active Form `1` feed. Keep this as a duplicate-source risk until disabled or proven audit-only.
- GTM Version `16` published the USA Meta dataset split: base pixel `1531247935333023`, host-scoped pageview trigger, and standard Meta `Lead` tags for both dispatch events.
- The old shared Meta pixel `918227085392601` was removed from the USA WordPress Insert Headers and Footers header/body options. A post-purge WordPress database search returned zero matches for that ID.
- GTM Version `17` paused old active GA4, Google Ads, and Meta email/phone/application-click tags while keeping base infrastructure, GAConnector, helper dispatch, GA4 `generate_lead`, and Meta `Lead` tags active.
- GTM Version `18` updated the two USA Meta `Lead` tags with an `fbq` init fallback.
- Meta custom conversion `1915200622465036` / `USA Franchise Lead` now exists on dataset `1531247935333023` for standard `Lead` plus the `/inquiry-thank-you/` success path.
- GTM Version `19` published trigger `269` and tag `270` to write GAConnector values into USA Form `1` and Form `2` hidden fields `14-30`.
- Post-Version-19 browser checks confirmed Form `1` and Form `2` fields `14-30` are populated from URL UTMs, `gclid`, GAConnector cookies, and `_ga` client ID before submission.

## Website Source

- [x] Confirm live Form 1 page renders `GTM-5LZMHBZL`.
- [x] Confirm live Form 2 page renders `GTM-5LZMHBZL`.
- [x] Confirm live Form 1 page renders WPCode bridge markers.
- [x] Confirm live Form 2 page renders WPCode bridge markers.
- [x] Confirm current Form 1 URL is `/available-opportunities/franchising-inquiry/`.
- [x] Confirm current Form 2 URL is `/partner-with-cefa/real-estate-partners/submit-a-site/`.
- [x] Confirm old test URLs `/franchise-application/` and `/real-estate-submission/` return `404` and are not current QA paths.
- [x] Confirm Form 1 website-side event is `franchise_inquiry_submit`.
- [x] Confirm Form 2 website-side event is `real_estate_site_submit`.
- [x] Confirm payload context uses `site_context=franchise_us`, `market=usa`, and `country=US` from controlled post-Version-15 submissions.

## GTM Version 15

- [x] Publish USA GTM Version `15`.
- [x] Hostname-scope helper triggers to `franchisecefa.com` and `www.franchisecefa.com`.
- [x] Require `site_context=franchise_us` on helper and dispatch triggers.
- [x] Add delayed dispatch events for Form 1 and Form 2.
- [x] Add GA4 `generate_lead` tags for Form 1 and Form 2.
- [x] Pause legacy Elementor/form-submit final GA4 tags.
- [x] Pause legacy Google Ads final tags pending USA-specific label confirmation.
- [x] Pause legacy Meta final tags pending USA-specific dataset/pixel confirmation.
- [x] Confirm live `gtm.js` contains the new dispatch and helper event names.

## GTM Version 16 - USA Meta

- [x] Publish USA GTM Version `16`.
- [x] Move USA Meta base pixel to dataset `1531247935333023`.
- [x] Hostname-scope the USA Meta base pixel to `franchisecefa.com` and `www.franchisecefa.com`.
- [x] Add Meta standard `Lead` tag for Form `1` dispatch event `cefa_franchise_us_inquiry_dispatch`.
- [x] Add Meta standard `Lead` tag for Form `2` dispatch event `cefa_franchise_us_site_dispatch`.
- [x] Pass `eventID` from the helper payload into Meta `Lead` tags.
- [x] Remove old shared Meta pixel `918227085392601` from USA WordPress Insert Headers and Footers options.
- [x] Confirm fresh public HTML has zero `918227085392601` occurrences after WP Engine cache purge.
- [x] Confirm fresh headless browser network check has a `1531247935333023` Meta config request and zero `918227085392601` Meta requests.
- [x] Create USA inquiry custom conversion `1915200622465036` / `USA Franchise Lead` for dataset `1531247935333023`.
- [ ] Confirm Meta Events Manager live `Lead` receipt for dataset `1531247935333023`.

## GTM Version 17 - Helper-Only Cleanup

- [x] Publish USA GTM Version `17`.
- [x] Pause old Google Ads click conversion tags `75`, `88`, and `92`.
- [x] Pause old Meta click tags `161`, `164`, and `167`.
- [x] Pause old GA4 click tags `203`, `206`, and `211`.
- [x] Keep Conversion Linker, Google/GA4 base tags, Google Ads remarketing, and GAConnector active.
- [x] Keep helper dispatch, GA4 `generate_lead`, Meta base, and Meta `Lead` tags active.
- [x] Confirm public `gtm.js` still contains `1531247935333023`, `G-YL1KQPWV0M`, `AW-11088792613`, and both USA dispatch events.
- [x] Confirm public `gtm.js` has zero old shared dataset `918227085392601` occurrences.
- [x] Confirm public `gtm.js` has zero legacy click markers: `fr_email_click`, `fr_phone_click`, `fr_application_click`, `Fr Email Click`, `Fr Phone Click`, and `Fr Application Click`.

## GTM Version 18 - Meta Lead Reliability

- [x] Publish USA GTM Version `18`.
- [x] Add `fbq` init fallback to Meta `Lead` tag `267`.
- [x] Add `fbq` init fallback to Meta `Lead` tag `268`.
- [x] Keep the USA dataset/pixel as `1531247935333023`.
- [x] Create Meta custom conversion `1915200622465036` / `USA Franchise Lead`.
- [ ] Confirm the next successful USA Form `1` submission appears as a `Lead` in Meta Events Manager for dataset `1531247935333023`.

## GTM Version 19 - Attribution Hidden Field Writer

- [x] Publish USA GTM Version `19`.
- [x] Add DOM Ready trigger `269`, scoped to `franchisecefa.com` and the two live USA Gravity Forms pages.
- [x] Add Custom HTML tag `270`, `CEFA - Franchise USA - GAConnector Hidden Field Writer`.
- [x] Confirm tag `270` does not push `dataLayer`.
- [x] Confirm tag `270` does not call `gtag`.
- [x] Confirm tag `270` does not call `fbq`.
- [x] Confirm Form `1` fields `14-30` populate from GAConnector/URL values.
- [x] Confirm Form `2` fields `14-30` populate from GAConnector/URL values.
- [ ] Submit controlled Form `1` entry and confirm saved Gravity Forms entry fields `14-30`.
- [ ] Submit controlled Form `2` entry and confirm saved Gravity Forms entry fields `14-30`.

## Post-Publish QA

- [x] Submit controlled Form 1 test after Version `15` propagation and confirm the helper and dispatch events.
- [x] Submit controlled Form 2 test after Version `15` propagation and confirm the helper and dispatch events.
- [x] Confirm Form 1 GA4 `generate_lead` browser hit or processed report row.
- [x] Confirm Form 2 GA4 `generate_lead` browser hit.
- [ ] Confirm Form 1 and Form 2 do not produce legacy `fr_us_apply_submit_success` final conversions.
- [ ] Confirm direct thank-you visits and reloads still do not push duplicate final events.
- [ ] Confirm GA4 processed report rows after delay. Realtime passed on 2026-05-04; same-day processed reports can lag.
- [x] Register USA GA4 custom dimensions for low-cardinality helper payload reporting fields.
- [x] Confirm GA4 property `519783092` is linked to Google Ads accounts `3820636025` and `4159217891`.
- [x] Confirm USA-related imported Google Ads conversion actions exist through reporting-query evidence.
- [ ] Confirm which Google Ads account and conversion action should be the USA bidding/primary action before activating Ads final helper-event tags.
- [x] Confirm and activate USA Meta dataset/pixel `1531247935333023` in GTM Version `16`.
- [x] Create USA Meta inquiry custom conversion `1915200622465036` / `USA Franchise Lead`.
- [ ] Confirm USA Meta Events Manager receipt for standard `Lead` on dataset `1531247935333023`.
- [ ] Confirm whether the USA GA4 property currency should remain `CAD`.
- [ ] Disable or prove audit-only the active Gravity Forms Google Analytics Form `1` feed.
- [x] Fix USA attribution mapping so helper payloads include populated UTM/click/GA client values when GAConnector cookies exist.
- [x] Fix USA browser hidden-field writer so Gravity Forms fields `14-30` are populated before submit.

## Measurement Protocol Audit Test

- [ ] If the Gravity Forms Google Analytics / Measurement Protocol add-on is tested, send an audit-only event such as `franchise_us_inquiry_submit_server_audit`, not a second GA4 `generate_lead`.
- [ ] Map `location_interest` using the lowercase parameter name exactly.
- [ ] Confirm the value resolves to the submitted answer for "Where are you interested in opening a CEFA school?", not the literal question label.
- [ ] Do not send name, email, phone, address, free-text notes, click IDs, full URLs, or other PII/high-cardinality values through the Measurement Protocol feed.
