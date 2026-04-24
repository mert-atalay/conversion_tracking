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
