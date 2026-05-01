# Live Form And CRM Integrity Review

Last updated: 2026-04-30

## Scope

The websites are live on their production domains. This review focused on whether the submission forms still render, submit, save the intended Gravity Forms values, and hand off CRM/Synuma attributes where the available tools can verify that.

No backend settings, WordPress files, GTM containers, GA4 properties, Ads accounts, Meta datasets, or Gravity Forms settings were changed.

Checked properties:

- Parent Canada: `https://cefa.ca`
- Franchise Canada: `https://franchise.cefa.ca`
- Franchise USA: `https://franchisecefa.com`

Evidence used:

- Controlled public browser submissions.
- Public DOM/form field inspection before submit.
- Live WordPress MCP saved-entry reads.
- Read-only SQL through the live franchise MCP control ability for `cefa_synuma_lead_id` entry meta.
- Browser redirect/success-page confirmation.

## Executive Findings

| Property | Form | Visible form | Saved entry | CRM/bridge proof | Status |
| --- | --- | --- | --- | --- | --- |
| `cefa.ca` | Parent Form `4` | Pass | Pass, entry `89` | Field `32.*` and attribution fields saved; KinderTales downstream not verified here | Form structure and CRM attributes intact at GF level |
| `franchise.cefa.ca` | Franchise Inquiry Form `1` | Pass | Pass, entry `30` | No `cefa_synuma_lead_id` found | Needs CRM bridge investigation |
| `franchise.cefa.ca` | Submit a Site Form `2` | Pass | Pass, entry `33` | `cefa_synuma_lead_id=1c1c5f8a-0e20-430e-8408-b43c0189b628` | Working |
| `franchisecefa.com` | Franchise Inquiry Form `1` | Pass, but mixed CA/US location options | Pass, entry `26` | `cefa_synuma_lead_id=290d4025-f0d0-4426-89bd-b43c018b497d` | Working, with location-list issue |
| `franchisecefa.com` | Submit a Site Form `2` | Pass | Pass, entry `27` | No `cefa_synuma_lead_id` found | Needs CRM bridge investigation |

## Parent Canada: `cefa.ca`

Test path:

```text
https://cefa.ca/submit-an-inquiry-today/?location=abbotsford-highstreet&utm_source=qa_form_review&utm_medium=live_qa&utm_campaign=form_integrity_20260430b&gclid=QA-FORM-GCLID-20260430B
```

Browser result:

- Form `4` rendered correctly on `Submit an Inquiry Today`.
- School context rendered as `Abbotsford - Highstreet`.
- Submitted successfully.
- Redirected to `/thank-you/?location=abbotsford-highstreet&inquiry=true`.

Live Gravity Forms entry:

- Entry ID: `89`
- Source URL: `https://cefa.ca/submit-an-inquiry-today/?location=abbotsford-highstreet`
- Email: `qa.parent.live.review.2+20260430@cefa.ca`

Confirmed Field `32` values:

- `32.1` school UUID: `81236954-bcad-11ef-8bcb-028d36469a89`
- `32.2` program ID: `475`
- `32.3` days per week: `5 days`
- `32.4` event ID: `ccb107ae-95ca-4e00-9d33-c5d0bdb28d5a`
- `32.5` school slug: `abbotsford-highstreet`
- `32.6` school name: `Abbotsford - Highstreet`
- `32.7` program name: `Junior Kindergarten 1`

Confirmed attribution fields:

- `35` utm_source: `qa_form_review`
- `36` utm_medium: `live_qa`
- `37` utm_campaign: `form_integrity_20260430b`
- `40` gclid: `QA-FORM-GCLID-20260430B`
- `45` first_landing_page: full landing URL with UTM/GCLID
- `46` first_referrer: `direct`

Parent verdict:

- The parent form is intact at the visible form and saved Gravity Forms level.
- The agreed school/program/day CRM attributes are saving cleanly.
- Attribution persistence is saving correctly into fields `35-46` for this test.
- This review did not verify KinderTales or downstream business delivery outside WordPress/GF.

## Franchise Canada: `franchise.cefa.ca`

### Form 1: Franchise Inquiry

Test path:

```text
https://franchise.cefa.ca/available-opportunities/franchising-inquiry/?utm_source=qa_form_review&utm_medium=live_qa&utm_campaign=franchise_ca_form_integrity_20260430&gclid=QA-FRCA-FORM-GCLID-20260430
```

Browser result:

- Form `1` rendered correctly.
- Required visible fields appeared.
- Conditional fields appeared after selecting cash range and location.
- Submitted successfully.
- Redirected to `/inquiry-thank-you/?location=edmonton-ab&inquiry=true`.

Live Gravity Forms entry:

- Entry ID: `30`
- Email: `qa.franchise.ca.live.review+20260430@cefa.ca`
- Cash: `More than $1,000,000`
- Location: `497`
- Ready timeframe: `6 - 9 Months`
- Schools: `1`
- Shareholder: `Sole Shareholder`
- Consent: `1`

CRM bridge proof:

- No `cefa_synuma_lead_id` entry meta was found after waiting and rechecking.

Verdict:

- The visible form and Gravity Forms saved entry are intact.
- Synuma/CRM delivery is not confirmed for this form and should be investigated.

### Form 2: Submit a Site

Test path:

```text
https://franchise.cefa.ca/partner-with-cefa/real-estate-partners/submit-a-site/?utm_source=qa_form_review&utm_medium=live_qa&utm_campaign=franchise_ca_site_form_integrity_20260430&gclid=QA-FRCA-SITE-FORM-GCLID-20260430
```

Browser result:

- Form `2` rendered correctly.
- Submitted successfully.
- Redirected to `/site-thank-you/`.

Live Gravity Forms entry:

- Entry ID: `33`
- Email: `qa.site.ca.live.review+20260430@cefa.ca`
- Company: `QA Property Holdings`
- Site offered by: `Developer`
- Square footage: `12,500-14,999 sq ft`
- Outdoor space: `6,250-7,499 sq ft`
- Country: `Canada`
- Availability: `Immediate`

CRM bridge proof:

- `cefa_synuma_lead_id=1c1c5f8a-0e20-430e-8408-b43c0189b628`

Verdict:

- Canada Form `2` is intact at visible form, saved entry, and Synuma/CRM bridge level.

## Franchise USA: `franchisecefa.com`

### Form 1: Franchise Inquiry

Test path:

```text
https://franchisecefa.com/available-opportunities/franchising-inquiry/?utm_source=qa_form_review&utm_medium=live_qa&utm_campaign=franchise_us_form_integrity_20260430&gclid=QA-FRUS-FORM-GCLID-20260430
```

Browser result:

- Form `1` rendered and submitted successfully.
- Conditional fields appeared after selecting cash range and location.
- Redirected to `/inquiry-thank-you/?location=atlanta&inquiry=true`.

Live Gravity Forms entry:

- Entry ID: `26`
- Email: `qa.franchise.us.live.review+20260430@cefa.ca`
- State: `Georgia`
- ZIP: `30303`
- Cash: `More than $1,000,000 USD`
- Location: `1190`
- Ready timeframe: `6-9 months`
- Schools: `1`
- Shareholder: `Sole Shareholder`
- Consent: `1`

CRM bridge proof:

- `cefa_synuma_lead_id=290d4025-f0d0-4426-89bd-b43c018b497d`

Issue:

- The USA franchise inquiry location dropdown contains both USA and Canada locations. USA options are present, but Canada options are also selectable.

Verdict:

- USA Form `1` is intact at visible form, saved entry, and Synuma/CRM bridge level.
- The mixed CA/US location list should be corrected or explicitly approved.

### Form 2: Submit a Site

Test path:

```text
https://franchisecefa.com/partner-with-cefa/real-estate-partners/submit-a-site/?utm_source=qa_form_review&utm_medium=live_qa&utm_campaign=franchise_us_site_form_integrity_20260430&gclid=QA-FRUS-SITE-FORM-GCLID-20260430
```

Browser result:

- Form `2` rendered correctly.
- Submitted successfully.
- Redirected to `/site-thank-you/`.

Live Gravity Forms entry:

- Entry ID: `27`
- Email: `qa.site.us.live.review+20260430@cefa.ca`
- Company: `QA US Property Holdings`
- Site offered by: `Developer`
- Square footage: `12,500-14,999 sq ft`
- Outdoor space: `6,250-7,499 sq ft`
- Country: `United States`
- Availability: `Immediate`

CRM bridge proof:

- No `cefa_synuma_lead_id` entry meta was found after waiting and rechecking.

Verdict:

- The visible form and Gravity Forms saved entry are intact.
- Synuma/CRM delivery is not confirmed for this form and should be investigated.

## Attribution Fields

Franchise Forms `1` and `2` on both Canada and USA had GAConnector-style hidden fields `14-30` present in the form HTML, but the live browser submissions saved those fields blank.

This means:

- Basic form submission and some CRM bridge paths can work without these fields.
- Attribution is not intact yet for public franchise browser submissions.
- The prior REST/API test entries that had attribution values do not prove that live browser submissions are carrying attribution.

Recommended next check:

- Confirm whether GAConnector is expected to populate fields `14-30` on the new live franchise sites.
- If yes, inspect script placement/load order and whether it reads the same field IDs after migration.
- If GAConnector remains unreliable, replace or supplement it with the CEFA-owned attribution persistence layer from the broader tracking plan.

## Priority Fix List

1. Investigate why Canada Form `1` entry `30` does not have `cefa_synuma_lead_id`.
2. Investigate why USA Form `2` entry `27` does not have `cefa_synuma_lead_id`.
3. Decide whether USA Form `1` should filter out Canada locations.
4. Fix or replace franchise attribution population for fields `14-30`.
5. After form/CRM integrity is confirmed, return to the conversion tracking bridge and GTM/GA4/Ads/Meta mapping work.

