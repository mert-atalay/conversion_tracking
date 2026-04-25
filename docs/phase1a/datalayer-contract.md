# DataLayer Payload Contract

Canonical website-side event:

```text
school_inquiry_submit
```

This is not the final GA4/Meta/Google Ads name. GTM maps it to destination events.

## Required Payload

```js
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: "school_inquiry_submit",
  event_id: "<same as Gravity Forms field 32.4>",
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
  inquiry_success: true,
  inquiry_success_url: window.location.href,
  page_context: "parent",
  tracking_source: "helper_plugin"
});
```

## Clean Value Rule

Each value must be separate. Do not emit the combined custom field string as any final parameter value.

## GTM Mapping

| Source event | Destination | Destination event |
|---|---|---|
| `school_inquiry_submit` | GA4 | `generate_lead` |
| `school_inquiry_submit` | Google Ads | parent inquiry conversion |
| `school_inquiry_submit` | Meta Pixel | `Lead` |
| `school_inquiry_submit` | Future server-side | same logical event with shared `event_id` |

## Micro-Conversion Contract

Phase 1A also uses plugin-owned browser micro-events for diagnostic reporting:

```text
parent_inquiry_cta_click
find_a_school_click
phone_click
email_click
form_start
form_submit_click
validation_error
```

These are not final lead conversions and should not be used for Google Ads bidding at launch.

All micro-events use a unique micro-event `event_id` plus structured metadata, for example:

```js
window.dataLayer.push({
  event: "parent_inquiry_cta_click",
  event_id: "<unique micro-event ID>",
  event_scope: "micro",
  page_context: "parent",
  page_type: "school",
  page_url: window.location.href,
  page_path: "/school/abbotsford-highstreet/",
  tracking_source: "helper_plugin",
  click_url: "<clicked URL>",
  click_text: "<clicked text>",
  cta_id: "<derived or data-cefa CTA ID>",
  cta_location: "header|hero|navigation|content|footer|unknown",
  lead_intent: "inquire_now",
  form_id: "4",
  form_family: "parent_inquiry",
  school_selected_slug: "<school slug if available>",
  inquiry_event_id: "<Form 4 field 32.4 when available>"
});
```

Do not add Universal Analytics-style `event_category`, `event_action`, `event_label`, or `event_title` as the event model. GA4 tags should use event names plus explicit parameters.
