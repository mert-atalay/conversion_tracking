# Naming Convention Workstream

This folder is for CEFA naming standards that affect paid media, creative files, UTMs, and automation.

## Current Source Of Truth

- Local summary: `/Users/matthewbison/Desktop/cefa-nexus/CEFA/.agency/context/cefa-meta-naming-convention-2026-04-28.md`
- Google Sheet mirror: documented in that local summary.
- Workbook remains the human source of truth unless CEFA approves a new naming version.
- Latest reviewed Drive package, candidate v19/NC2: [Drive folder](https://drive.google.com/drive/folders/1uVG9KM-C94covrmZqle20ja4NJKC3taZ) and [v19 workbook](https://docs.google.com/spreadsheets/d/1n4SehWNb6UfhNDkYtKyYOS19a-v_Eijq/edit?usp=drivesdk&ouid=100264075182330360487&rtpof=true&sd=true).
  - Status: `Partial`
  - The v19 package is reviewed as a budget-driven candidate. It should not replace NC1 until CEFA approves the campaign-pattern change and the Meta import status guardrail is resolved.

## Current Naming Version

Current Meta naming version: `NC1`.
Current local listing UTM version: `ll1`.
Budget-driven Meta naming v19 is a candidate future version, not the approved current version.

Key contracts:

- Campaign: `CEFA | {ScopeTag} | {FundingTag} | {ActivationTag} | {SchoolOrGroup} | META | {Objective} | {Funnel} | {Theme} | {YYYYMM} | {Seq}`
- Ad set: `{Persona} | {AudienceType} | {Geo} | {Placement}`
- Meta ad: `{FormatTag} | {VisualConcept} | {CopyAngle} | v{AdVersion}`
- Creative group key: `{school_slug}__{scope}__{funding}__{activation}__{theme}__{format}__{concept}__cr##__v#`
- UTM: `utm_source=meta&utm_medium=paid_social&utm_campaign={campaign_slug}&utm_content={ad_slug_or_data_key}`

## Current Files

- [Budget-driven Meta naming v19 review](./budget-driven-meta-naming-v19-review-2026-05-04.md)
  - Status: `Partial`
  - Covers the latest Drive package links, v19 naming rules, n8n phase-1 guardrails, and open approval risks.
- [Local listing UTM rules - GBP and Yelp](./local-listing-utm-rules-gbp-yelp-2026-05-03.md)
  - Status: `Partial`
  - Covers GBP/Yelp website and inquiry-form UTM rules.
  - The rule is approved for documentation use, but live listing updates still require field availability and school-slug verification.

## BigQuery / Dashboard Registry

- Current naming-convention rule references are available to dashboards through `marketing-api-488017.mart_marketing.vw_measurement_rule_registry_current`.
- The BigQuery implementation is documented in [Dashboard source layer, GreenRope, and rule registry](../20-bigquery/dashboard-source-layer-greenrope-and-rule-registry-2026-05-03.md).
- The workbook or mirrored Google Sheet remains the human source of truth for Meta NC1. Do not treat the dashboard registry as permission to change NC1 token meanings.

## Rules

- Do not silently change token meanings.
- Do not use Drive/SharePoint creative filenames as visible Meta ad names.
- API-created or imported Meta objects must default to paused unless explicitly approved.
- Paid-media agents should link here before creating or reviewing campaign/ad naming.

## Suggested Next Files

- `nc1-current-contract.md`
- `utm-standard.md`
- `creative-filename-taxonomy.md`
- `n8n-naming-guardrails.md`
