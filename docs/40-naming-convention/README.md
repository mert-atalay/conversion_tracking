# Naming Convention Workstream

This folder is for CEFA naming standards that affect paid media, creative files, UTMs, and automation.

## Current Source Of Truth

- Local summary: `/Users/matthewbison/Desktop/cefa-nexus/CEFA/.agency/context/cefa-meta-naming-convention-2026-04-28.md`
- Google Sheet mirror: documented in that local summary.
- Workbook remains the human source of truth unless CEFA approves a new naming version.
- Latest reviewed Drive package, final v3 / v20 candidate: [Drive folder](https://drive.google.com/drive/folders/1OYm5c2hA7UZF3AXk5XvOvIcMq6g-P_qN) and [v20 workbook](https://docs.google.com/spreadsheets/d/1A2WmOmADovTHV69zt9kA5KtBWoatAJOD/edit?usp=drivesdk&ouid=100264075182330360487&rtpof=true&sd=true).
  - Status: `Partial`
  - Formula placement in the budget tabs was fixed in the live Drive workbook on 2026-05-04. The v20/final-v3 package has the right dynamic-copy direction, but it is not ready as the governed source of truth until URL/UTM source mapping, dropdown validation, location/form URL reconciliation, and the active-object rename inventory is reviewed by CEFA.
- Current POC control sheet: [CEFA Paid Media Build Control Center - POC v1 - 2026-05-05](https://docs.google.com/spreadsheets/d/11mlcPQy_nz-XvjgSotl0cCWAJr2BS8REK6Ex2nOIMYI/edit).
  - Status: `Partial`
  - Created as the simpler team-facing control surface for copy, creative, budget reference, ID-backed destinations, build manifest rows, QA, and future n8n/import output.
  - This is not a live launch or budget-edit tool.
- Latest successful Meta bulk import pattern: [Meta bulk import success pattern - 2026-05-05](./meta-bulk-import-success-pattern-2026-05-05.md).
  - Status: `Verified` for user-confirmed successful Ads Manager bulk import of the Franchise Canada video refresh.
  - Status: `Partial` for the observed WhatsApp/browser add-on behavior, because the controlling setting or import column is not verified yet.
  - Status: `Pending` for future ad-level tags, because eligibility was observed but export/import or API read/write behavior is not verified yet.
- Latest reviewed Drive package, candidate v19/NC2: [Drive folder](https://drive.google.com/drive/folders/1uVG9KM-C94covrmZqle20ja4NJKC3taZ) and [v19 workbook](https://docs.google.com/spreadsheets/d/1n4SehWNb6UfhNDkYtKyYOS19a-v_Eijq/edit?usp=drivesdk&ouid=100264075182330360487&rtpof=true&sd=true).
  - Status: `Partial`
  - The v19 package is reviewed as a budget-driven candidate. It should not replace NC1 until CEFA approves the campaign-pattern change and the Meta import status guardrail is resolved.

## Current Naming Version

Current live Meta naming version: `NC1`.
Current proposed Meta naming version for review/renaming: `NC2`.
Current proposed Google Ads naming version for review/renaming: `GADS1`.
Current local listing UTM version: `ll1`.
Budget-driven Meta naming v20/final-v3 and the active-object inventory are the current NC2 planning surfaces, not live rename approval.

Key contracts:

- Campaign: `CEFA | {BudgetScope} | {Activation} | {LocationOrGroup} | META | {Objective} | {Funnel} | {Theme} | {YYYYMM} | {Seq}`
- Ad set: `{Persona} | {AudienceType} | {Geo} | {Placement}`
- Meta ad: `{FormatTag} | {ProgramOrTopic} | {VisualConcept} | {CopyAngle} | v{AdVersion}`
- Google Ads campaign: `CEFA | {BudgetScope} | {Activation} | {LocationOrGroup} | GOOGLE | {Channel} | {Objective} | {Funnel} | {Theme} | {YYYYMM} | {Seq}`
- Google Ads search ad group: `{PersonaOrIntent} | {KeywordTheme} | {GeoOrMarket} | {MatchStrategy}`
- Google Ads PMax asset group: `Asset Group | {GeoOrMarket} | PMax`
- Creative group key: `{school_slug}__{scope}__{funding}__{activation}__{theme}__{format}__{concept}__cr##__v#`
- UTM: `utm_source=meta&utm_medium=paid_social&utm_campaign={campaign_key}&utm_content={ad_data_key}&utm_term={ad_set_key}`
- Google Ads UTM: `utm_source=google&utm_medium=cpc&utm_campaign={campaign_key}&utm_content={ad_build_key}&utm_term={keyword_or_ad_group_key}`
- Rename/join handle: use `campaign_id`, `adset_id`, and `ad_id` from the active-object inventory. Do not use current names as the only live object selector.
- Build/import handle: use a row-level build manifest that maps creative, copy, URL tags, program/topic, campaign/ad set/ad IDs, QA, and approval status before any Meta import or n8n write.

## Current Files

- [Meta naming NC2 active last-30 inventory](./meta-naming-nc2-active-last-30-inventory-2026-05-04.md)
  - Status: `Verified` for live Meta reads and active object IDs/names; `Partial` for proposed NC2 names.
  - Covers CEFA Early Learning and CEFA Franchisor campaigns, ad sets, and ads that delivered from 2026-04-05 through 2026-05-04.
  - Links the active object inventory CSV with current names, campaign/ad set/ad IDs, parent campaign/ad set IDs, proposed NC2 names, and review flags.
- [Meta creative build import manifest contract](./meta-creative-build-import-manifest-2026-05-04.md)
  - Status: `Partial`
  - Defines the row-level workbook/n8n contract required before mapping CEFA creative and copy into Meta campaign/ad set/ad create, update, or rename rows.
  - Requires ID-based object matching, parent program-token dropdowns, separate franchise topics, generated URL tags, QA gates, approval status, and `PAUSED` import defaults.
- [Google Ads naming GADS1 active last-30 inventory](./google-ads-naming-gads1-active-last-30-inventory-2026-05-04.md)
  - Status: `Verified` for live Google Ads reads and active object IDs/names; `Partial` for proposed GADS1 names.
  - Covers CEFA $3000 and CEFA Franchisor campaigns, ad groups, asset groups, and ads that delivered from 2026-04-05 through 2026-05-04.
  - Links the active object inventory CSV with current names, campaign/ad group/asset group/ad IDs, proposed GADS1 names, and review flags.
- [Paid media build control center POC](./paid-media-build-control-center-poc-2026-05-05.md)
  - Status: `Partial`
  - Documents the new native Google Sheet POC for team copy/creative intake, budget sync, ID-backed object destinations, build manifest QA, and future n8n/import output.
- [Meta bulk import success pattern](./meta-bulk-import-success-pattern-2026-05-05.md)
  - Status: `Verified` for the user-confirmed successful Franchise Canada video bulk import pattern.
  - Records the reusable live-status-safe CSV pattern, the WhatsApp/browser add-on follow-up, and the pending ad-level tag opportunity.
- [Budget-driven Meta naming v20 final-v3 review](./budget-driven-meta-naming-v20-final-v3-review-2026-05-04.md)
  - Status: `Partial`
  - Covers the final-v3 Drive package, dynamic copy improvements, and blocking workbook fixes before team rollout.
- [Budget-driven Meta naming v19 review](./budget-driven-meta-naming-v19-review-2026-05-04.md)
  - Status: `Partial`
  - Covers the latest Drive package links, v19 naming rules, n8n phase-1 guardrails, and open approval risks.
- [Local listing UTM rules - GBP and Yelp](./local-listing-utm-rules-gbp-yelp-2026-05-03.md)
  - Status: `Partial`
  - Covers GBP/Yelp website and inquiry-form UTM rules.
  - The rule is approved for documentation use, but live listing updates still require field availability and school-slug verification.

## Related Master Data Inputs

- [School form programs Google Sheet source](../60-master-data/school-form-programs-google-sheet-source-2026-05-04.md)
  - Status: `Partial`
  - Use as a parent-school program and form URL input for future parent `ProgramTag` dropdowns after reconciliation against the canonical school dimension.

## BigQuery / Dashboard Registry

- Current naming-convention rule references are available to dashboards through `marketing-api-488017.mart_marketing.vw_measurement_rule_registry_current`.
- The BigQuery implementation is documented in [Dashboard source layer, GreenRope, and rule registry](../20-bigquery/dashboard-source-layer-greenrope-and-rule-registry-2026-05-03.md).
- The workbook or mirrored Google Sheet remains the human source of truth for Meta NC1. Do not treat the dashboard registry as permission to change NC1 token meanings.

## Rules

- Do not silently change token meanings.
- Do not use Drive/SharePoint creative filenames as visible Meta ad names.
- Do not rename live Meta objects by name lookup alone; use IDs from the active-object inventory.
- Do not rename live Google Ads objects by name lookup alone; use customer, campaign, ad group, asset group, and ad IDs from the Google Ads inventory.
- Do not treat Google Ads ads as having a Meta-style visible ad name; use `ad_id` plus a build key for ad-level tracking and bulk edits.
- Do not build Meta import rows directly from creative files or copy text alone; use the build manifest contract so every row has destination, copy, creative, URL tag, QA, and approval fields.
- API-created or imported Meta objects must default to paused unless explicitly approved.
- API-created or bulk-created Google Ads campaigns, ad groups, asset groups, and ads must default to paused unless explicitly approved.
- Paid-media agents should link here before creating or reviewing campaign/ad naming.

## Suggested Next Files

- `nc1-current-contract.md`
- `utm-standard.md`
- `creative-filename-taxonomy.md`
- `n8n-naming-guardrails.md`
