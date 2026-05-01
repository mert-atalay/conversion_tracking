# Franchise USA GTM Build And QA Notes

Last updated: 2026-05-01

## Published GTM Version

- Account: `6004334435` / `CEFA Franchise`
- Container: `204988779` / `GTM-5LZMHBZL`
- Published version: `15`
- Version name: `CEFA Franchise USA Phase 1 helper-event GA4 mapping - 2026-05-01`

## New Helper Event Flow

Form 1:

```text
franchise_inquiry_submit
-> CEFA - Franchise USA - franchise_inquiry_submit helper
-> CEFA - Franchise USA - dispatch inquiry helper event
-> cefa_franchise_us_inquiry_dispatch
-> CEFA - GA4 - Franchise USA - generate_lead - inquiry
```

Form 2:

```text
real_estate_site_submit
-> CEFA - Franchise USA - real_estate_site_submit helper
-> CEFA - Franchise USA - dispatch site helper event
-> cefa_franchise_us_site_dispatch
-> CEFA - GA4 - Franchise USA - generate_lead - site
```

## Host And Context Containment

The new helper triggers require:

- `Page Hostname` matches `^(www\.)?franchisecefa\.com$`
- `site_context=franchise_us`
- `market=usa`

The dispatch triggers also require:

- `site_context=franchise_us`
- `form_family=franchise_inquiry` for Form 1
- `form_family=site_inquiry` for Form 2

## New GTM Entities

Triggers:

- `258` / `CEFA - Franchise USA - franchise_inquiry_submit helper`
- `259` / `CEFA - Franchise USA - real_estate_site_submit helper`
- `260` / `CEFA - Franchise USA - inquiry dispatch`
- `261` / `CEFA - Franchise USA - site dispatch`

Tags:

- `262` / `CEFA - Franchise USA - dispatch inquiry helper event`
- `263` / `CEFA - Franchise USA - dispatch site helper event`
- `264` / `CEFA - GA4 - Franchise USA - generate_lead - inquiry`
- `265` / `CEFA - GA4 - Franchise USA - generate_lead - site`

Data layer variables:

- `229` / `DLV - cefa - event_id`
- `230` / `DLV - cefa - site_context`
- `231` / `DLV - cefa - business_unit`
- `232` / `DLV - cefa - market`
- `233` / `DLV - cefa - country`
- `234` / `DLV - cefa - form_id`
- `235` / `DLV - cefa - form_family`
- `236` / `DLV - cefa - lead_type`
- `237` / `DLV - cefa - lead_intent`
- `238` / `DLV - cefa - tracking_source`
- `239` / `DLV - cefa - location_interest`
- `240` / `DLV - cefa - investment_range`
- `241` / `DLV - cefa - opening_timeline`
- `242` / `DLV - cefa - school_count_goal`
- `243` / `DLV - cefa - ownership_structure`
- `244` / `DLV - cefa - site_offered_by`
- `245` / `DLV - cefa - property_square_footage_range`
- `246` / `DLV - cefa - outdoor_space_range`
- `247` / `DLV - cefa - availability_timeline`
- `248` / `DLV - cefa - lc_source`
- `249` / `DLV - cefa - lc_medium`
- `250` / `DLV - cefa - lc_campaign`
- `251` / `DLV - cefa - fc_source`
- `252` / `DLV - cefa - fc_medium`
- `253` / `DLV - cefa - fc_campaign`
- `254` / `DLV - cefa - inquiry_success_url`
- `255` / `DLV - cefa - event_scope`
- `256` / `DLV - cefa - lc_channel`
- `257` / `DLV - cefa - fc_channel`

## Legacy Final Tags Paused

These USA tags were paused in Version `15` because they use old Elementor/form-submit paths or shared-pixel final events and could duplicate the new helper-event source:

- `220` / `Franchisor_GA4_Fr Application Submit_ollo`
- `210` / `Franchisor_GA4_Fr Site Form Submit_ollo`
- `218` / `Franchisor_GAds_Fr Application Submit_ollo`
- `53` / `Franchisor_GAds_Fr Site Form Submit_ollo`
- `226` / `Franchisor_FB_Fr Application Submit_ollo`
- `159` / `Franchisor_FB_Site Form Submit_ollo`
- `225` / `cHTML - Fr Apply Success Listener (USA)_ollo`

Base pageview, Google tag, conversion linker, remarketing, and non-final tags were left unchanged.

## Verification Completed

- GTM MCP auth confirmed.
- USA container Version `15` was created and published.
- Live `gtm.js?id=GTM-5LZMHBZL` contains:
  - `G-YL1KQPWV0M`
  - `franchise_inquiry_submit`
  - `real_estate_site_submit`
  - `cefa_franchise_us_inquiry_dispatch`
  - `cefa_franchise_us_site_dispatch`
- Live Form 1 page renders `GTM-5LZMHBZL`, `cefa-franchise-conversion`, `franchise_inquiry_submit`, and `wpcode_bridge`.
- Live Form 2 page renders `GTM-5LZMHBZL`, `cefa-franchise-conversion`, `real_estate_site_submit`, and `wpcode_bridge`.

## Still Needed

- Controlled post-Version-15 Form 1 submission and GA4 realtime/reporting confirmation.
- Controlled post-Version-15 Form 2 submission and GA4 realtime/reporting confirmation.
- USA GA4 custom dimensions for low-cardinality helper fields.
- USA Google Ads conversion action/label confirmation before activating Ads final tags.
- USA Meta dataset/pixel confirmation before activating Meta final tags.
- Decision on whether USA GA4 property currency should remain `CAD`.
