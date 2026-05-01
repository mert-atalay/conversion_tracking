# Live Conversion Tracking Status

Last updated: 2026-05-01

## Scope

This note records the current production-domain state after the parent live cutover and the first franchise live tracking bridge pass.

Checked properties:

- Parent Canada: `https://cefa.ca`
- Franchise Canada: `https://franchise.cefa.ca`
- Franchise USA: `https://franchisecefa.com`

## Executive Status

| Property | Website-side source | GTM/platform mapping | Status |
| --- | --- | --- | --- |
| `cefa.ca` | CEFA Conversion Tracking plugin | Active through `GTM-NZ6N7WNC` | Parent Phase 1A website/GTM path is working. |
| `franchise.cefa.ca` | WPCode fallback bridge + GAConnector selector map | Active through `GTM-TPJGHFS` Version `52` | Canada Phase 1 website/GTM path is working for Forms 1 and 2. |
| `franchisecefa.com` | WPCode fallback bridge | Pending final mapping | Forms 1 and 2 now push confirmed-success dataLayer events. |

## Parent Canada Current State

The parent live runtime is:

- Active GTM container: `GTM-NZ6N7WNC`
- Old parent GTM container: `GTM-PPV9ZRZ`, archived/reference-only
- WordPress source: `CEFA Conversion Tracking` plugin
- Tested live plugin version: `0.4.1`
- Repository plugin version after follow-up code changes: `0.4.2`
- Canonical parent event: `school_inquiry_submit`

Current parent result:

- One successful Form 4 submission creates one `school_inquiry_submit`.
- The browser `event_id` matches Gravity Forms field `32.4`.
- Field `32.3` days per week is not overwritten by the tracking plugin anymore.
- The saved multi-day value remains comma-separated for the business path.
- The dataLayer payload normalizes legacy pipe-delimited day values only for reporting.
- Attribution fields `35` through `46` are populated through the CEFA-owned attribution bridge.
- Direct thank-you visits and thank-you reloads do not push the final primary event.
- GTM maps the helper-plugin event to GA4/Google Ads/Meta.

Guardrail:

- Do not reactivate the Gravity Forms Google Analytics Add-On as a second final conversion source.
- Do not map parent final conversions from the old `GTM-PPV9ZRZ` container.
- Do not use the School Manager business fields as tracking write targets beyond the approved `32.4` event ID field.

## Franchise Bridge Deployment

The franchise sites currently use a WPCode fallback bridge instead of the full plugin package because direct PHP plugin-file writes were blocked in the live hosting path.

Source file:

- `snippets/franchise-wpcode-bridge.php`

The fallback bridge:

- registers a one-time REST payload endpoint at `/wp-json/cefa-franchise-conversion/v1/payload/<event_id>`
- hooks Gravity Forms Form `1` and Form `2`
- stores the tracking `event_id` in Gravity Forms entry meta `cefa_conversion_tracking_event_id`
- appends `cefa_tracking=1` and `cefa_tracking_event_id=<uuid>` to successful confirmation URLs
- fetches the confirmed payload from the thank-you page with `POST` and `cache: no-store`
- consumes the server payload after one successful fetch
- pushes the final dataLayer event only after confirmed submission
- reads GAConnector fields `14` through `30` when present
- does not overwrite GAConnector, Synuma, SiteZeus, CRM delivery, notifications, or form UI behavior

Current public render check:

| URL | HTTP | GTM | Bridge markers |
| --- | --- | --- | --- |
| `https://franchise.cefa.ca/available-opportunities/franchising-inquiry/` | 200 | `GTM-TPJGHFS` | `cefa-franchise-conversion`, `franchise_inquiry_submit`, `POST`, `no-store`, `wpcode_bridge` |
| `https://franchise.cefa.ca/partner-with-cefa/real-estate-partners/submit-a-site/` | 200 | `GTM-TPJGHFS` | `cefa-franchise-conversion`, `real_estate_site_submit`, `POST`, `no-store`, `wpcode_bridge` |
| `https://franchisecefa.com/available-opportunities/franchising-inquiry/` | 200 | `GTM-5LZMHBZL` | `cefa-franchise-conversion`, `franchise_inquiry_submit`, `POST`, `no-store`, `wpcode_bridge` |
| `https://franchisecefa.com/partner-with-cefa/real-estate-partners/submit-a-site/` | 200 | `GTM-5LZMHBZL` | `cefa-franchise-conversion`, `real_estate_site_submit`, `POST`, `no-store`, `wpcode_bridge` |

## Franchise Canada Evidence

Runtime:

- Domain: `franchise.cefa.ca`
- GTM: `GTM-TPJGHFS`
- Published GTM version: `52` / `CEFA Franchise Canada Phase 1 helper-event mapping - 2026-05-01`
- GA4 property: `259747921` / `CEFA Franchise`
- Linked Google Ads customer: `3820636025`
- Meta pixel/dataset kept on the existing shared franchise pixel: `918227085392601`
- LinkedIn partner ID kept as `4536524`

GTM implementation:

- Raw helper events remain `franchise_inquiry_submit` and `real_estate_site_submit`.
- GTM adds a short delayed dispatch event before firing platform tags:
  - `cefa_franchise_inquiry_dispatch`
  - `cefa_real_estate_site_dispatch`
- The dispatch layer prevents lost destination hits when the confirmed helper event arrives before destination libraries are fully ready.
- Existing destination IDs were preserved instead of creating new platform learning surfaces.
- GAConnector tag `GA Connector - CRM` was updated to map GAConnector cookie values into Gravity Forms hidden fields `14` through `30` for Form `1` and Form `2`.

Form 1 / Franchise Inquiry:

- Final website event: `franchise_inquiry_submit`
- Dispatch event for destination tags: `cefa_franchise_inquiry_dispatch`
- Latest validated event ID: `77b52ed9-2ffe-42ef-b98a-293c27ed4d13`
- Event ID storage: Gravity Forms entry meta `cefa_conversion_tracking_event_id`
- Payload context: `site_context=franchise_ca`, `market=canada`, `country=CA`, `form_id=1`, `form_family=franchise_inquiry`, `lead_type=franchise_lead`
- Confirmed non-PII lead metadata included location interest/name, investment range, opening timeline, school count goal, and ownership structure.
- Confirmed attribution fields saved/pushed cleanly: `lc_source`, `lc_medium`, `lc_campaign`, `lc_content`, `lc_term`, `lc_channel`, `lc_landing`, `lc_referrer`, `fc_source`, `fc_medium`, `fc_campaign`, `fc_content`, `fc_term`, `fc_channel`, `fc_referrer`, `gclid`, and `ga_client_id`.
- Confirmed GA4/Google measurement hit for `generate_lead`.
- Confirmed Google Ads conversion hit for conversion ID `11088792613`, label `MfYYCITslY4YEKWYxqcp`.
- Confirmed Meta custom event `Fr Inquiry Submit` on pixel `918227085392601` with matching `event_id`.
- Confirmed LinkedIn conversion ID `11308340` with matching `event_id`.
- Direct payload request after browser consumption returned `404`.
- Thank-you reload did not push another final event.

Form 2 / Submit a Site:

- Final website event: `real_estate_site_submit`
- Dispatch event for destination tags: `cefa_real_estate_site_dispatch`
- Latest validated event ID: `5462203a-7857-4de0-93b9-fa83a5b61b94`
- Event ID storage: Gravity Forms entry meta `cefa_conversion_tracking_event_id`
- Payload context: `site_context=franchise_ca`, `market=canada`, `country=CA`, `form_id=2`, `form_family=site_inquiry`, `lead_type=real_estate_lead`
- Confirmed non-PII site metadata included site offered by, square-footage range, outdoor-space range, and availability timeline.
- Confirmed GA4 `generate_lead` hit with site-submission metadata.
- Confirmed Google Ads conversion hits for conversion ID `11088792613`, label `vq7GCIrslY4YEKWYxqcp`, and conversion ID `802334988`, label `lZGsCLenuvgCEIzSyv4C`.
- Confirmed Meta custom event `Fr Site Form Submit` on pixel `918227085392601` with matching `event_id`.
- Confirmed LinkedIn conversion ID `11308348` with matching `event_id`.
- Direct payload request after browser consumption returned `404`.

## Franchise USA Evidence

Runtime:

- Domain: `franchisecefa.com`
- GTM: `GTM-5LZMHBZL`
- GA4 property: `519783092` / `CEFA Franchise - USA.`
- Linked Google Ads customers: `3820636025`, `4159217891`
- GA4 currency currently: `CAD`

Form 1 / Franchise Inquiry:

- Final event: `franchise_inquiry_submit`
- Gravity Forms entry: `30`
- Event ID: `d88a8105-7fe9-446e-9c90-91badf3c6848`
- Event ID storage: Gravity Forms entry meta `cefa_conversion_tracking_event_id`
- Payload context: `site_context=franchise_us`, `market=usa`, `country=US`, `form_id=1`, `form_family=franchise_inquiry`, `lead_type=franchise_lead`
- Confirmed non-PII lead metadata included location interest/name, investment range, opening timeline, school count goal, and ownership structure.
- Direct payload request after browser consumption returned `404`.
- Thank-you reload did not push another final event.

Form 2 / Submit a Site:

- Final event: `real_estate_site_submit`
- Gravity Forms entry: `31`
- Event ID: `47c301dd-2797-4a9e-981c-28e14175d90a`
- Event ID storage: Gravity Forms entry meta `cefa_conversion_tracking_event_id`
- Payload context: `site_context=franchise_us`, `market=usa`, `country=US`, `form_id=2`, `form_family=site_inquiry`, `lead_type=real_estate_lead`
- Confirmed non-PII site metadata included site offered by, square-footage range, outdoor-space range, and availability timeline.
- Direct payload request after browser consumption returned `404`.

## GA4 Admin Status

Parent `267558140`:

- Phase 1A event-scoped custom dimensions for the parent helper-plugin payload are registered.
- `generate_lead` already exists as a key event.

Franchise Canada `259747921`:

- Property exists and is linked to Google Ads customer `3820636025`.
- Custom dimensions are still mostly legacy/reporting fields such as `event_title`, `event_label`, `preferred_location`, `applicant_capital`, page/click fields, and video fields.
- The new helper-plugin franchise parameters are not fully registered yet.

Franchise USA `519783092`:

- Property exists and is linked to Google Ads customers `3820636025` and `4159217891`.
- No custom dimensions or custom metrics are currently registered.
- Currency is currently `CAD`; confirm whether that should remain or change before production reporting signoff.

## What Is Still Pending

Franchise Canada Phase 1 browser/platform mapping is now working from live browser evidence. Remaining items are admin/reporting cleanup and the USA build.

Pending work:

- Evaluate GA4 Measurement Protocol as a Phase 1B audit-only server-side event, not as a duplicate `generate_lead` source.
- Register GA4 custom dimensions for the new franchise payloads in the Canada GA4 property.
- Confirm the new events appear in GA4 reports/realtime after processing delay.
- Confirm Google Ads conversion action primary/secondary settings before bidding decisions.
- Confirm Meta Events Manager receives the events and create/adjust franchise-specific custom conversions inside the current shared dataset.
- Hostname-scope USA tags to `franchisecefa.com` and `www.franchisecefa.com`.
- Build USA GTM destination mappings after Canada signoff.
- Disable or demote legacy thank-you/pageview/form-auto triggers so they cannot duplicate final conversions.
- Monitor GTM cache propagation; clean contexts loaded Version `52` correctly.

## Current Interpretation

Parent Canada is complete enough to keep live and monitor.

Franchise Canada is now Phase 1 browser/platform functional: confirmed-success website events, attribution writeback, dispatch-layer GTM mapping, and live destination hits are verified. It still needs GA4 custom dimensions and platform UI confirmation before reporting signoff.

Franchise USA still has the confirmed-success website-side dataLayer source, but destination mappings, custom dimensions, and duplicate-source suppression still need to be built and retested.

Measurement Protocol remains a Phase 1B strengthening layer. If tested through the Gravity Forms Google Analytics Add-On, it should first send an audit-only event such as `school_inquiry_submit_server_audit` with the same `event_id`, not a second GA4 `generate_lead`.
