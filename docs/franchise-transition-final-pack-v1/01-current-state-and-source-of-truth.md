# Current State And Source Of Truth

## Parent current state

Parent staging:

```text
https://cefamain.kinsta.cloud
```

Production target:

```text
https://cefa.ca
```

Current parent website-side event:

```text
school_inquiry_submit
```

GA4 destination event:

```text
generate_lead
```

Current parent helper plugin:

```text
CEFA Conversion Tracking
Version: 0.3.0
```

Current parent staging GTM container:

```text
GTM-NZ6N7WNC
```

Current parent GA4 property:

```text
Main Site - GA4
properties/267558140
```

Current parent event contract:

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: "school_inquiry_submit",
  event_id: "<same as Form 4 field 32.4>",
  form_id: "4",
  form_family: "parent_inquiry",
  lead_type: "cefa_lead",
  lead_intent: "inquire_now",
  school_selected_id: "<32.1>",
  school_selected_slug: "<32.5>",
  school_selected_name: "<32.6>",
  program_id: "<32.2>",
  program_name: "<32.7>",
  days_per_week: "<32.3>",
  utm_source: "<35>",
  utm_medium: "<36>",
  utm_campaign: "<37>",
  utm_term: "<38>",
  utm_content: "<39>",
  gclid: "<40>",
  gbraid: "<41>",
  wbraid: "<42>",
  fbclid: "<43>",
  msclkid: "<44>",
  first_landing_page: "<45>",
  first_referrer: "<46>",
  inquiry_success: true,
  inquiry_success_url: window.location.href,
  page_context: "parent",
  tracking_source: "helper_plugin"
});
```

## Franchise staging surfaces

Franchise Canada staging:

```text
https://cefafranchise.kinsta.cloud
```

Expected production host:

```text
https://franchise.cefa.ca
```

Franchise USA staging:

```text
https://cefafranusdev.wpenginepowered.com
```

Expected production host:

```text
https://www.franchisecefa.com
```

## Source-of-truth principles

### Website-side truth

Each site family should expose a neutral website-side event:

```text
parent: school_inquiry_submit
franchise Canada: franchise_inquiry_submit
franchise USA: franchise_us_inquiry_submit or franchise_inquiry_submit with market=usa
site submission: real_estate_site_submit
```

### GTM truth

GTM maps neutral website events to destination events.

Examples:

```text
school_inquiry_submit -> GA4 generate_lead
franchise_inquiry_submit -> GA4 generate_lead
franchise_inquiry_submit -> Meta Lead
real_estate_site_submit -> GA4 generate_lead or custom site_submission event
```

### Meta truth during transition

For Canada franchise, the currently optimized dataset should stay active temporarily if live campaigns rely on it.

For USA franchise, default to a clean separate dataset before serious optimization.

### Long-term truth

The long-term state should be separated by business funnel:

```text
Parent enrollment
Franchise Canada B2B
Franchise USA B2B
```
