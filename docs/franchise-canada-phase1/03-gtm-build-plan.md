# Franchise Canada GTM Build Plan

Last updated: 2026-04-29

## Current Container

- Account: `6004334435`
- Container: `48104535`
- Public ID: `GTM-TPJGHFS`
- Workspace: `48` / `Default Workspace`

The new staging site currently loads the same container as the current/live Canada franchise website. This creates risk if new tags are not hostname-contained.

## Recommended GTM Implementation Path

Phase 1 should use a new GTM workspace in the existing Canada franchise container unless CEFA decides to replace the site snippet with a separate clean container.

Workspace name:

```text
CEFA Franchise Canada Phase 1 Tracking - 2026-04
```

Initial trigger containment:

```text
Page Hostname equals cefafranchise.kinsta.cloud
```

Production containment after cutover:

```text
Page Hostname equals franchise.cefa.ca
```

Do not create broad all-pages platform tags without hostname filters while staging and live old site share `GTM-TPJGHFS`.

## Variables To Create

Create dataLayer variables for all primary payload fields.

Core variables:

- `DLV - event_id`
- `DLV - event_scope`
- `DLV - site_context`
- `DLV - business_unit`
- `DLV - market`
- `DLV - country`
- `DLV - form_id`
- `DLV - form_family`
- `DLV - lead_type`
- `DLV - lead_intent`
- `DLV - inquiry_success`
- `DLV - event_source_url`
- `DLV - inquiry_success_url`
- `DLV - page_path`
- `DLV - page_title`
- `DLV - tracking_source`

Franchise inquiry variables:

- `DLV - location_interest`
- `DLV - location_availability_status`
- `DLV - investment_range`
- `DLV - opening_timeline`
- `DLV - school_count_goal`
- `DLV - ownership_structure`

Real estate site variables:

- `DLV - site_offered_by`
- `DLV - property_square_footage_range`
- `DLV - outdoor_space_range`
- `DLV - availability_timeline`

Attribution variables:

- `DLV - lc_source`
- `DLV - lc_medium`
- `DLV - lc_campaign`
- `DLV - lc_content`
- `DLV - lc_term`
- `DLV - lc_channel`
- `DLV - lc_landing`
- `DLV - lc_referrer`
- `DLV - fc_source`
- `DLV - fc_medium`
- `DLV - fc_campaign`
- `DLV - fc_content`
- `DLV - fc_term`
- `DLV - fc_channel`
- `DLV - fc_referrer`
- `DLV - gclid`
- `DLV - ga_client_id`

## Triggers To Create

Primary custom event triggers:

- `CEFA CA - Event - franchise_inquiry_submit`
  - Custom event: `franchise_inquiry_submit`
  - Conditions:
    - `DLV - site_context` equals `franchise_ca`
    - `DLV - form_id` equals `1`
    - `Page Hostname` equals staging or production hostname for the current phase
- `CEFA CA - Event - real_estate_site_submit`
  - Custom event: `real_estate_site_submit`
  - Conditions:
    - `DLV - site_context` equals `franchise_ca`
    - `DLV - form_id` equals `2`
    - `Page Hostname` equals staging or production hostname for the current phase

Micro triggers:

- `CEFA CA - Event - franchise_cta_click`
- `CEFA CA - Event - franchise_form_start`
- `CEFA CA - Event - franchise_form_submit_attempt`
- `CEFA CA - Event - franchise_form_validation_error`
- `CEFA CA - Event - franchise_location_select`
- `CEFA CA - Link - phone_click`
- `CEFA CA - Link - email_click`
- `CEFA CA - Link - file_download`
- `CEFA CA - Link - outbound_click`

## Tags To Create

Base tags:

- GA4 Google tag for `G-6EMKPZD7RD`, hostname-contained.
- Conversion Linker, hostname-contained.
- Meta base pixel only after confirming dataset transition decision.

Primary destination tags:

- GA4 event tag for `franchise_inquiry_submit`
  - GA4 event name: `generate_lead`
  - Include `event_id` and the non-PII metadata fields.
- GA4 event tag for `real_estate_site_submit`
  - GA4 event name: `generate_lead` or `site_submission_submit` depending on final reporting decision.
  - Include `event_id` and the non-PII metadata fields.
- Meta Lead for Form 1 and Form 2 only after dataset decision is confirmed.
- Google Ads conversion tags only after the exact conversion action labels are confirmed.

Micro reporting tags:

- GA4 events for CTA clicks, form starts, submit attempts, validation errors, phone/email clicks, file downloads, outbound clicks, video engagement, and newsletter signup.
- Do not send these as Google Ads bidding conversions at launch.

## What Not To Copy From Old GTM

Do not copy:

- old thank-you pageview-only final conversion triggers
- Elementor form class triggers
- old path-specific triggers such as `own-a-cefa`
- broad click-text triggers without hostname and URL containment
- old schema/SEO injections
- unmanaged attribution cookie Custom HTML if the helper plugin owns attribution

## Build Gate

Before publishing:

- Confirm one and only one final primary event fires per successful Form 1 submission.
- Confirm one and only one final primary event fires per successful Form 2 submission.
- Confirm direct thank-you page visits do not fire primary events.
- Confirm old live host `franchise.cefa.ca` is not affected during staging tests.
- Confirm Meta dataset strategy before mapping Meta `Lead`.
- Confirm Google Ads conversion labels before mapping Ads conversions.

