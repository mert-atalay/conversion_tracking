# Franchise Canada Event Taxonomy And DataLayer Contracts

Last updated: 2026-04-29

## Naming Rule

Website events stay neutral. GTM maps them to GA4, Google Ads, Meta, and future CAPI/sGTM destinations.

Do not hard-code platform event names such as GA4 `generate_lead` into the website/plugin event name.

## Primary Events

### `franchise_inquiry_submit`

Confirmed successful submission of Form `1` / `Franchise Inquiry`.

Destination mapping:

- GA4: `generate_lead`
- Meta: `Lead`
- Google Ads: Canada franchise inquiry conversion action
- BigQuery/collector later: accepted lead event

Required payload:

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: "franchise_inquiry_submit",
  event_id: "<unique per successful submission>",
  event_scope: "primary",
  site_context: "franchise_ca",
  business_unit: "franchise",
  market: "canada",
  country: "CA",
  form_id: "1",
  form_family: "franchise_inquiry",
  lead_type: "franchise_lead",
  lead_intent: "franchise_inquiry",
  inquiry_success: true,
  event_source_url: window.location.href,
  inquiry_success_url: window.location.href,
  page_path: window.location.pathname,
  page_title: document.title,
  location_interest: "<selected location / field 32 value if non-PII and available>",
  location_availability_status: "available|not_available|unknown",
  investment_range: "<field 7>",
  opening_timeline: "<field 10>",
  school_count_goal: "<field 11>",
  ownership_structure: "<field 12>",
  tracking_source: "helper_plugin"
});
```

### `real_estate_site_submit`

Confirmed successful submission of Form `2` / `Site Inquiry`.

Destination mapping:

- GA4: `generate_lead` or a separate GA4 event if CEFA wants real-estate reporting split at event-name level.
- Meta: `Lead` or custom conversion rule based on event name and `lead_type`.
- Google Ads: Canada real-estate/site inquiry conversion action if configured.

Required payload:

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: "real_estate_site_submit",
  event_id: "<unique per successful submission>",
  event_scope: "primary",
  site_context: "franchise_ca",
  business_unit: "franchise",
  market: "canada",
  country: "CA",
  form_id: "2",
  form_family: "site_inquiry",
  lead_type: "real_estate_lead",
  lead_intent: "submit_a_site",
  inquiry_success: true,
  event_source_url: window.location.href,
  inquiry_success_url: window.location.href,
  page_path: window.location.pathname,
  page_title: document.title,
  site_offered_by: "<field 39>",
  property_square_footage_range: "<field 34>",
  outdoor_space_range: "<field 35>",
  availability_timeline: "<field 36>",
  tracking_source: "helper_plugin"
});
```

## Attribution Parameters

Where present, include these values from the existing hidden fields in Form `1` and Form `2`.

Last click fields:

- `lc_source`
- `lc_medium`
- `lc_campaign`
- `lc_content`
- `lc_term`
- `lc_channel`
- `lc_landing`
- `lc_referrer`

First click fields:

- `fc_source`
- `fc_medium`
- `fc_campaign`
- `fc_content`
- `fc_term`
- `fc_channel`
- `fc_referrer`

Click/client ID fields:

- `gclid`
- `ga_client_id`

Recommended dataLayer additions:

```js
{
  lc_source: "<field 14>",
  lc_medium: "<field 15>",
  lc_campaign: "<field 16>",
  lc_content: "<field 17>",
  lc_term: "<field 18>",
  lc_channel: "<field 19>",
  lc_landing: "<field 20>",
  lc_referrer: "<field 21>",
  fc_source: "<field 22>",
  fc_medium: "<field 23>",
  fc_campaign: "<field 24>",
  fc_content: "<field 25>",
  fc_term: "<field 26>",
  fc_channel: "<field 27>",
  fc_referrer: "<field 28>",
  gclid: "<field 29>",
  ga_client_id: "<field 30>"
}
```

## Micro-Conversions

Use these for GA4 reporting and funnel diagnostics. Keep them out of Google Ads bidding at launch unless CEFA explicitly approves.

- `franchise_cta_click`
- `franchise_form_start`
- `franchise_form_submit_attempt`
- `franchise_form_validation_error`
- `franchise_location_select`
- `phone_click`
- `email_click`
- `file_download`
- `outbound_click`
- `video_engagement`
- `newsletter_signup_submit`

Recommended common micro payload:

```js
{
  event: "franchise_cta_click",
  event_id: "<unique micro-event ID>",
  event_scope: "micro",
  site_context: "franchise_ca",
  business_unit: "franchise",
  market: "canada",
  country: "CA",
  page_path: window.location.pathname,
  page_title: document.title,
  click_url: "<click URL>",
  click_text: "<safe click text>",
  cta_family: "franchise_inquiry|real_estate_site|phone|email|download|outbound",
  tracking_source: "gtm_or_helper_plugin"
}
```

## PII Rule

Do not pass these values to dataLayer, GA4, Google Ads, Meta, or GTM variables:

- first name
- last name
- phone
- email
- full street address
- company contact details
- free-text availability details

Use non-PII categorical fields only.

