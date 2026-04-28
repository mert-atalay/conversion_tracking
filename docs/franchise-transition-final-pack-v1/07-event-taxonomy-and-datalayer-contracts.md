# Franchise Event Taxonomy And DataLayer Contracts

## Naming principle

Website events should be neutral business events.

GTM maps them to destination-specific names.

Do not hardcode final platform behavior in the website.

## Parent event

```text
school_inquiry_submit
```

## Franchise Canada events

```text
franchise_inquiry_submit
real_estate_site_submit
franchise_contact_submit
```

## Franchise USA events

Recommended:

```text
franchise_inquiry_submit
real_estate_site_submit
franchise_contact_submit
```

Differentiate with:

```text
site_context = franchise_us
market = usa
country = US
```

## Franchise inquiry payload

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: "franchise_inquiry_submit",
  event_id: "<unique per submission>",
  form_id: "<form id>",
  form_name: "<form name>",
  form_family: "franchise_inquiry",
  lead_type: "franchise_lead",

  site_context: "franchise_ca", // or franchise_us
  business_unit: "franchise",
  market: "canada", // or usa
  country: "CA", // or US

  page_type: "<page type>",
  page_group: "<page group>",
  inquiry_success: true,
  inquiry_success_url: window.location.href,
  event_source_url: window.location.href,
  tracking_source: "<gtm|helper_plugin|form_addon>"
});
```

## Real estate / submit-a-site payload

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: "real_estate_site_submit",
  event_id: "<unique per submission>",
  form_id: "<form id>",
  form_name: "<form name>",
  form_family: "site_submission",
  lead_type: "real_estate_lead",

  site_context: "franchise_ca", // or franchise_us
  business_unit: "franchise",
  market: "canada", // or usa
  country: "CA", // or US

  page_type: "real_estate",
  inquiry_success: true,
  inquiry_success_url: window.location.href,
  event_source_url: window.location.href,
  tracking_source: "<gtm|helper_plugin|form_addon>"
});
```

## CTA payload

```js
window.dataLayer.push({
  event: "franchise_inquiry_cta_click",
  site_context: "franchise_ca",
  business_unit: "franchise",
  market: "canada",
  cta_id: "<cta id>",
  cta_location: "<hero|nav|body|footer>",
  page_type: "<page type>",
  page_group: "<page group>",
  click_url: "<destination URL>"
});
```

## GTM destination mapping

| Website event | GA4 | Meta | Google Ads |
|---|---|---|---|
| `franchise_inquiry_submit` | `generate_lead` | `Lead` | Franchise inquiry conversion |
| `real_estate_site_submit` | `generate_lead` or `site_submission_submit` | `Lead` or custom conversion | Site submission conversion |
| `franchise_inquiry_cta_click` | reporting event | optional reporting only | no bidding at launch |
| `download_click` | reporting event | optional reporting only | no bidding at launch |
