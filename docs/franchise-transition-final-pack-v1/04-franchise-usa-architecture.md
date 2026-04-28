# Franchise USA Tracking Architecture

## Surface

Staging:

```text
https://cefafranusdev.wpenginepowered.com
```

Production target:

```text
https://www.franchisecefa.com
```

Business role:

```text
B2B franchise / investor / real-estate lead generation in the United States
```

## Final recommendation

Use a separate measurement boundary by default.

USA should not inherit the parent Canada or franchise Canada Meta dataset unless there is an existing live campaign dependency that must be protected temporarily.

## Preferred website-side events

Two acceptable naming patterns:

### Option A — USA-specific event names

```text
franchise_us_inquiry_submit
franchise_us_site_submit
```

### Option B — shared franchise event names + market parameter

```text
franchise_inquiry_submit
real_estate_site_submit
market = "usa"
country = "US"
site_context = "franchise_us"
```

Recommended choice:

```text
Option B
```

Reason: simpler GTM templates and cleaner cross-market reporting while preserving market separation in parameters and destination mapping.

## Required event parameters

```js
{
  site_context: "franchise_us",
  business_unit: "franchise",
  market: "usa",
  country: "US",
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

## Meta

Recommended:

```text
Separate USA Meta dataset/pixel before serious optimization
```

Reason:

- different domain
- different country
- different sales motion
- cleaner diagnostics
- cleaner CAPI later
- cleaner compliance and reporting boundary

If any USA campaigns currently optimize against the shared dataset, audit first and do not break active campaigns blindly. For new production optimization, use the USA dataset.

## GA4 and GTM

Recommended:

- separate GA4 property for franchise USA
- dedicated USA GTM web container
- dedicated Meta dataset/pixel
- dedicated Google Ads conversion action family
