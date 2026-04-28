# Franchise Canada Tracking Architecture

## Surface

Staging:

```text
https://cefafranchise.kinsta.cloud
```

Production:

```text
https://franchise.cefa.ca
```

Business role:

```text
B2B franchise / investor / real-estate lead generation in Canada
```

## Final recommendation

Use a dedicated franchise tracking contract.

Do not copy parent school logic into franchise.

## Preferred website-side events

```text
franchise_inquiry_submit
real_estate_site_submit
franchise_contact_submit
```

Optional micro-events:

```text
franchise_inquiry_cta_click
site_submission_cta_click
download_click
contact_click
resource_view
faq_expand
process_step_view
```

## Required event parameters

### Shared franchise parameters

```js
{
  site_context: "franchise_ca",
  business_unit: "franchise",
  market: "canada",
  country: "CA",
  form_family: "<franchise_inquiry|site_submission|contact>",
  lead_type: "<franchise_lead|real_estate_lead|general_contact>",
  event_id: "<unique per submission>",
  event_source: "website",
  event_source_url: window.location.href,
  tracking_source: "<gtm|helper_plugin|form_addon>",
  page_type: "<page type>",
  page_group: "<page group>",
  cta_id: "<cta id if available>",
  cta_location: "<cta location if available>"
}
```

### Optional fields if present on form

```js
{
  desired_market: "<province/region/city>",
  investment_range: "<range if collected>",
  availability_status: "<available|market_unavailable|unknown>",
  form_id: "<form id>",
  form_name: "<form name>"
}
```

Do not include sensitive or unnecessary form details in ad-platform payloads.

## GTM architecture

Recommended:

```text
Dedicated franchise Canada GTM web container
```

Acceptable short-term fallback:

```text
Shared GTM account/container only if every tag is strictly host-scoped
```

Required GTM host variable:

```text
{{Page Hostname}} equals franchise.cefa.ca
```

For staging:

```text
{{Page Hostname}} equals cefafranchise.kinsta.cloud
```

## GA4

Use a separate GA4 property or at minimum a separate data stream/property boundary for franchise Canada.

Recommended event mapping:

```text
franchise_inquiry_submit -> GA4 generate_lead
real_estate_site_submit -> GA4 generate_lead or site_submission_submit
```

## Meta

Do not abruptly split live Canada franchise campaigns away from the current shared dataset if campaigns are optimizing against it.

Transition path:

1. Keep current shared dataset temporarily for active campaigns.
2. Add `site_context=franchise_ca`, `business_unit=franchise`, `market=canada`, and `lead_type=franchise_lead`.
3. Create Meta custom conversions inside the current shared dataset.
4. Create/test separate franchise Canada dataset in parallel.
5. Move new or duplicated campaigns first.
6. Move active optimization only after volume and event quality are stable.
