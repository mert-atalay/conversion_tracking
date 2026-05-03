# Naming Convention Workstream

This folder is for CEFA naming standards that affect paid media, creative files, UTMs, and automation.

## Current Source Of Truth

- Local summary: `/Users/matthewbison/Desktop/cefa-nexus/CEFA/.agency/context/cefa-meta-naming-convention-2026-04-28.md`
- Google Sheet mirror: documented in that local summary.
- Workbook remains the human source of truth unless CEFA approves a new naming version.

## Current Naming Version

Current Meta naming version: `NC1`.
Current local listing UTM version: `ll1`.

Key contracts:

- Campaign: `CEFA | {ScopeTag} | {FundingTag} | {ActivationTag} | {SchoolOrGroup} | META | {Objective} | {Funnel} | {Theme} | {YYYYMM} | {Seq}`
- Ad set: `{Persona} | {AudienceType} | {Geo} | {Placement}`
- Meta ad: `{FormatTag} | {VisualConcept} | {CopyAngle} | v{AdVersion}`
- Creative group key: `{school_slug}__{scope}__{funding}__{activation}__{theme}__{format}__{concept}__cr##__v#`
- UTM: `utm_source=meta&utm_medium=paid_social&utm_campaign={campaign_slug}&utm_content={ad_slug_or_data_key}`

## Current Files

- [Local listing UTM rules - GBP and Yelp](./local-listing-utm-rules-gbp-yelp-2026-05-03.md)
  - Status: `Partial`
  - Covers GBP/Yelp website and inquiry-form UTM rules.
  - The rule is approved for documentation use, but live listing updates still require field availability and school-slug verification.

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
