# Franchise GAConnector Shadow Rollout

Date: 2026-07-20  
Production observation start: `2026-07-20 18:00:00 UTC` (`11:00 PDT`)  
Properties: `franchise.cefa.ca`, `franchisecefa.com`, and `www.franchisecefa.com`

## Purpose

Run the CEFA-owned canonical attribution system beside GAConnector long enough to measure whether it can safely replace GAConnector later. This is an evidence-only rollout. GAConnector remains the operational owner of Gravity Forms fields `14-30` and Synuma/SiteZeus continues to receive the existing payload.

## Live Configuration

CEFA Conversion Tracking `0.6.3` is active on Franchise Canada and Franchise USA with these guarded settings:

| Setting | Canada | USA |
|---|---|---|
| `CEFA_CT_RUNTIME_PROFILE` | `attribution_only` | `attribution_only` |
| `CEFA_CT_ATTRIBUTION_V2_MODE` | `shadow` | `shadow` |
| `CEFA_CT_LEDGER_MODE` | `shadow` | `shadow` |
| `CEFA_CT_CRM_IDENTITY_ENABLED` | `false` | `false` |
| `CEFA_CT_PAYLOAD_V2_ENABLED` | `false` | `false` |
| `CEFA_CT_COLLECTOR_ENABLED` | `false` | `false` |
| Host-specific attribution and ledger signing secrets | Present | Present |

Release ZIP SHA-256: `57b9c18bdb450b7c0dbfed43fdefa353a72d175cea3b15a3bb0764b281b1123f`.

The runtime captures an allowlisted, signed first-party attribution envelope and an opaque ledger reference. On a successful Form `1` or Form `2` submission it may write only these separate Gravity Forms entry-meta records:

- `cefa_conversion_tracking_attribution_v1`
- `cefa_conversion_tracking_schema_version`
- `cefa_conversion_tracking_delivery_status`
- `cefa_conversion_tracking_attribution_provenance`
- `cefa_conversion_tracking_writeback_status`
- `cefa_conversion_tracking_capture_id`
- `cefa_conversion_tracking_ledger_status`
- `cefa_conversion_tracking_attribution_parity_v1`

It does not write form fields `14-30`, create or promote an event ID, alter the Synuma payload, emit confirmation events, or send GA4, Google Ads, or Meta conversions in this profile.

## Before-State Baseline

Active entries during the 30 days immediately before rollout:

| Property / form | Entries | Legacy source present | Legacy GCLID present | Legacy GA client ID present | Canonical shadow present |
|---|---:|---:|---:|---:|---:|
| Canada Form 1 | 51 | 44 | 7 | 50 | 0 |
| Canada Form 2 | 6 | 6 | 0 | 6 | 0 |
| USA Form 1 | 24 | 21 | 0 | 24 | 0 |
| USA Form 2 | 7 | 6 | 0 | 7 | 0 |

The live WPCode option sizes remained unchanged after rollout: Canada `40,498` bytes and USA `43,236` bytes. Existing validation, conversion bridge, and Synuma recovery snippets remain active. No GTM, GA4, Google Ads, Meta, campaign, form, or CRM setting was changed.

## Production QA

The reusable test is `tools/franchise-shadow-browser-qa.js`. It opens the real form without submitting it and checks the public config, plugin script, hidden capture token, final dataLayer events, and platform conversion requests.

All four live form paths passed on 2026-07-20:

| Property / form | Correct context and modes | Capture token | REST status | Final events | Platform submit conversions |
|---|---|---|---:|---:|---:|
| Canada Form 1 | Pass | Present | `200` | 0 | 0 |
| Canada Form 2 | Pass | Present | `200` | 0 | 0 |
| USA Form 1 | Pass | Present | `200` | 0 | 0 |
| USA Form 2 | Pass | Present | `200` | 0 | 0 |

The deployment QA created only ledger rows: Canada `5`, USA `2`. It created zero Gravity Forms entries and therefore zero Synuma leads. A normal Google `/wcm` page-view bootstrap request was observed and excluded from submit-conversion detection because it has no final conversion label.

## Observation Contract

Run `tools/wp-shadow-parity-report.php` read-only for Forms `1` and `2` on both properties, starting at `2026-07-20 18:00:00 UTC`. Report only aggregate counts; do not export attribution values or lead PII.

Monitor:

- canonical attribution and opaque capture-reference coverage;
- paid-entry source, medium, campaign, channel, click-ID, and GA client-ID parity against fields `14-30`;
- mismatch categories without raw values;
- existing Synuma delivery-note outcomes and any new failures;
- duplicate final events or destination conversions;
- in-house marker isolation on USA traffic.

Initial health can be assessed after several days, but GAConnector must not be replaced until there is at least seven days of evidence and enough paid entries to evaluate. The cutover gate is:

- at least `98%` paid core-field parity after approved intentional-difference exclusions;
- at least `95%` canonical capture coverage for non-direct entries;
- zero duplicate conversion dispatch;
- zero new Synuma delivery regression;
- zero USA in-house false positives;
- an approved field-by-field mapping and rollback window.

Direct entries without acquisition evidence are expected to remain without a canonical envelope and must not be counted as a capture failure.

## Rollback

If any delivery or conversion regression appears, deactivate `cefa-conversion-tracking` on the affected franchise property. GAConnector, WPCode, GTM, and Synuma remain intact and continue to own the production flow. Pre-rollout managed-config backups are stored outside the web roots as:

- Canada: `/home/wpe-user/wp-config.cefa-shadow-before-20260720-ca.bak`
- USA: `/home/wpe-user/wp-config.cefa-shadow-before-20260720-us.bak`

Do not expose or copy the signing-secret values into GitHub or an evidence export.
