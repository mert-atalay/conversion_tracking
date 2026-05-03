# Franchise USA Post-Version-15 QA Evidence

Last updated: 2026-05-03

This note records the controlled USA franchise QA pass after `GTM-5LZMHBZL` Version `15` was live.

## Live URL Check

Current production form URLs:

| Form | URL | HTTP | Runtime |
| --- | --- | --- | --- |
| Form `1` / Franchise Inquiry | `https://franchisecefa.com/available-opportunities/franchising-inquiry/` | `200` | `GTM-5LZMHBZL` and WPCode bridge markers present |
| Form `2` / Submit a Site | `https://franchisecefa.com/partner-with-cefa/real-estate-partners/submit-a-site/` | `200` | `GTM-5LZMHBZL` and WPCode bridge markers present |

Older working-test paths are no longer current:

| URL | HTTP | Note |
| --- | --- | --- |
| `https://franchisecefa.com/franchise-application/` | `404` | Not a current QA URL |
| `https://franchisecefa.com/real-estate-submission/` | `404` | Not a current QA URL |

## Published GTM Runtime Check

Fresh `gtm.js` check for `GTM-5LZMHBZL` on 2026-05-03 found:

- `franchise_inquiry_submit`
- `real_estate_site_submit`
- `cefa_franchise_us_inquiry_dispatch`
- `cefa_franchise_us_site_dispatch`
- `G-YL1KQPWV0M`

This confirms the published runtime still contains the USA helper-event, dispatch, and GA4 destination markers.

## Controlled Form 1 Submission

Test URL:

`https://franchisecefa.com/available-opportunities/franchising-inquiry/?utm_source=codex&utm_medium=qa&utm_campaign=franchise_us_form1_qa_20260503&utm_content=tracking_readiness&utm_term=franchise_tracking_test&gclid=TEST-GCLID-US-F1-20260503`

Result:

- Thank-you URL: `https://franchisecefa.com/inquiry-thank-you/?location=atlanta&inquiry=true&cefa_tracking=1&cefa_tracking_event_id=4adf41e8-0f00-4051-acb5-0ad780fe84f1`
- Final helper event: `franchise_inquiry_submit`
- Dispatch event: `cefa_franchise_us_inquiry_dispatch`
- Event ID: `4adf41e8-0f00-4051-acb5-0ad780fe84f1`
- Payload context: `site_context=franchise_us`, `market=usa`, `country=US`, `form_id=1`, `form_family=franchise_inquiry`, `lead_type=franchise_lead`, `tracking_source=helper_plugin`
- Non-PII lead metadata observed: `location_interest=1190`, `investment_range=$850,000 - $950,000 USD`, `opening_timeline=6-9 months`, `school_count_goal=1`, `ownership_structure=Sole Shareholder`

Important note:

- The submitted `location_interest` value was the field value `1190`, not the visible label `Atlanta, GA`. If the Gravity Forms Measurement Protocol add-on is used for audit-only testing, it should send the lowercase parameter `location_interest` with the submitted value, not the question label.

## Controlled Form 2 Submission

Test URL:

`https://franchisecefa.com/partner-with-cefa/real-estate-partners/submit-a-site/?utm_source=codex&utm_medium=qa&utm_campaign=franchise_us_form2_qa_20260503&utm_content=tracking_readiness&utm_term=site_tracking_test&gclid=TEST-GCLID-US-F2-20260503`

Result:

- Thank-you URL: `https://franchisecefa.com/site-thank-you/?cefa_tracking=1&cefa_tracking_event_id=75716e51-70bd-4023-be4e-eec4f32ea468`
- Final helper event: `real_estate_site_submit`
- Dispatch event: `cefa_franchise_us_site_dispatch`
- Event ID: `75716e51-70bd-4023-be4e-eec4f32ea468`
- Payload context: `site_context=franchise_us`, `market=usa`, `country=US`, `form_id=2`, `form_family=site_inquiry`, `lead_type=real_estate_lead`, `tracking_source=helper_plugin`
- Non-PII site metadata observed: `site_offered_by=Developer`, `property_square_footage_range=12,500-14,999 sq ft`, `outdoor_space_range=6,250-7,499 sq ft`, `availability_timeline=Immediate`

Browser resource evidence after the Form 2 thank-you page loaded showed a GA4 request to `G-YL1KQPWV0M` with:

- Event name: `generate_lead`
- Event ID: `75716e51-70bd-4023-be4e-eec4f32ea468`
- `site_context=franchise_us`
- `business_unit=franchise`
- `market=usa`
- `country=US`
- `form_id=2`
- `form_family=site_inquiry`
- `lead_type=real_estate_lead`
- `lead_intent=submit_a_site`
- `tracking_source=helper_plugin`
- `value=250`
- Currency: `USD`

Base Google tag and remarketing/config requests for `AW-11088792613` were also present, but this is not proof that a final Google Ads lead conversion is active. USA final Google Ads helper-event tags remain intentionally blocked until the correct account and conversion action decision is made.

## GA4 API Follow-Up

GA4 Data API checks on 2026-05-03:

- Property `519783092` / `CEFA Franchise - USA.`
- Date range `2026-05-01` through `2026-05-03`
- Filter: `eventName=generate_lead`
- Result: no processed rows at the time of the check.

Realtime API check for `generate_lead`, helper events, and dispatch events also returned no rows at the time of verification.

Interpretation:

- Website source and GTM runtime mapping are live.
- Form 2 has browser-level GA4 hit evidence.
- Processed GA4 reporting is still pending and should be rechecked after the GA4 processing delay.

## Google Ads Readiness Check

GA4 property `519783092` is linked to:

- `3820636025` / CEFA Franchisor
- `4159217891` / CEFA `$3000`

Supermetrics Google Ads reporting queries on 2026-05-03 confirmed USA-related imported GA4 conversion actions exist in both linked accounts, but they are secondary and have zero all-conversion volume in the queried period:

| Account | Conversion action | Tracker ID | Primary for goal | All conversions |
| --- | --- | --- | --- | --- |
| `3820636025` | `Application Submit (USA)` | `7482298930` | `true` | `0` |
| `3820636025` | `CEFA Franchise - USA. (web) generate_lead` | `7499744287` | `false` | `0` |
| `3820636025` | `CEFA Franchise - USA. (web) ads_conversion_submit_lead_form` | `7482257746` | `false` | `0` |
| `4159217891` | `CEFA Franchise - USA. (web) generate_lead` | `7499970414` | `false` | `0` |
| `4159217891` | `Cefafranchise.com | Request Info Submission` | `293368274` | `false` | `0` |

Recommendation for ad-readiness:

- Use the browser/GTM/GA4 path for analytics observation now.
- Do not switch bidding to a USA final conversion until one account owner confirms which Google Ads account and conversion action should be optimized.
- If ads must launch immediately, keep final lead tracking under close QA and do not treat the existing zero-volume USA actions as fully proven bidding signals until processed GA4/Ads evidence appears.
