# Franchise USA QA And Cutover Checklist

Last updated: 2026-05-01

## Website Source

- [x] Confirm live Form 1 page renders `GTM-5LZMHBZL`.
- [x] Confirm live Form 2 page renders `GTM-5LZMHBZL`.
- [x] Confirm live Form 1 page renders WPCode bridge markers.
- [x] Confirm live Form 2 page renders WPCode bridge markers.
- [x] Confirm Form 1 website-side event is `franchise_inquiry_submit`.
- [x] Confirm Form 2 website-side event is `real_estate_site_submit`.
- [x] Confirm payload context uses `site_context=franchise_us`, `market=usa`, and `country=US` from controlled pre-Version-15 submissions.

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

## Post-Publish QA

- [ ] Submit controlled Form 1 test after Version `15` propagation and confirm one GA4 `generate_lead`.
- [ ] Submit controlled Form 2 test after Version `15` propagation and confirm one GA4 `generate_lead`.
- [ ] Confirm Form 1 and Form 2 do not produce legacy `fr_us_apply_submit_success` final conversions.
- [ ] Confirm direct thank-you visits and reloads still do not push duplicate final events.
- [ ] Confirm GA4 report processing after delay.
- [x] Register USA GA4 custom dimensions for low-cardinality helper payload reporting fields.
- [ ] Confirm Google Ads USA conversion action labels before activating Ads final helper-event tags.
- [ ] Confirm USA Meta dataset/pixel before activating Meta final helper-event tags.
- [ ] Confirm whether the USA GA4 property currency should remain `CAD`.

## Measurement Protocol Audit Test

- [ ] If the Gravity Forms Google Analytics / Measurement Protocol add-on is tested, send an audit-only event such as `franchise_us_inquiry_submit_server_audit`, not a second GA4 `generate_lead`.
- [ ] Map `location_interest` using the lowercase parameter name exactly.
- [ ] Confirm the value resolves to the submitted answer for "Where are you interested in opening a CEFA school?", not the literal question label.
- [ ] Do not send name, email, phone, address, free-text notes, click IDs, full URLs, or other PII/high-cardinality values through the Measurement Protocol feed.
