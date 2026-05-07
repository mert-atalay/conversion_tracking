# Paid Media Build Control Center v21 Final POC

Last updated: 2026-05-07

## Scope

| Field | Value |
| --- | --- |
| Workstream | `docs/40-naming-convention/` |
| Platform scope | Meta Ads and Google Ads naming, copy, creative, build manifest, and paused import output |
| Google Sheet | [CEFA Paid Media Naming Convention Build Control - v21 Final POC - 2026-05-06](https://docs.google.com/spreadsheets/d/15MkgHS4YQLFMAsZDleJytIIsLn-bupUJBELWmykuN6U/edit) |
| Drive folder | [v21 new folder](https://drive.google.com/drive/folders/1K9-BRXFjFONIpGNq8phLcnnPRF6Cyan8) |
| Source handoff | `CEFA_v21_Final_Agent_Handoff_Naming_Bulk_Dynamic_Copy_n8n.md` |
| Source blueprint | `CEFA_n8n_Budget_Driven_Meta_Google_Blueprint_v21.json` |
| Created with | Personal Google CLI / API under `yigitmertatalay@gmail.com` |
| Live platform writes made | No |

## Status

`Verified`

- The existing v21 Google Sheet was repaired and finalized in place; no duplicate sheet was created.
- The workbook now has simplified user-facing tabs for parent copy, franchise copy, parent rendered copy, franchise rendered copy, parent creative, franchise creative, parent builds, and franchise builds.
- Google Ads now has separate user-facing copy and build tabs: `GOOGLE_PARENT_RSA_CW`, `GOOGLE_FRANCHISE_RSA_CW`, `GOOGLE_PARENT_BUILD_MB`, and `GOOGLE_FRANCHISE_BUILD_MB`.
- Google Search RSA copy is no longer forced into the Meta copy shape. The Google copy tabs support 15 headline template fields, 4 description template fields, path fields, preview columns, QA, and approval.
- `GOOGLE_IMPORT_READY` now outputs the expanded Google RSA structure with 15 headline fields and 4 description fields.
- The original master tabs for copy templates, rendered copy, creative assets, and build manifest are now hidden backend consolidation tabs.
- `CAMPAIGN_PICKER` gives MB and the team readable campaign choices such as `LSM-003 | Parent LSM | META | Cornerstone | Enrollment | 2026-07`; the generated slot value remains the budget-plan key. It now also includes Google parent/franchise picker columns.
- `PARENT_COPY_CW`, `FRANCHISE_COPY_CW`, `GOOGLE_PARENT_RSA_CW`, `GOOGLE_FRANCHISE_RSA_CW`, `PARENT_CREATIVE_GD`, and `FRANCHISE_CREATIVE_GD` now start with `location_or_market` so content and design can see the target location/market before writing copy or preparing creative.
- `PARENT_RENDER_MB` and `FRANCHISE_RENDER_MB` now start with three human selectors: `month`, `location_or_market`, and `copy_template_picker`. The hidden `campaign_picker`, `campaign_slot`, `copy_template_slot`, and `copy_render_slot` are still generated for stable formulas.
- For the first POC, the visible `month` dropdown is limited to `2026-04` and `2026-05`. The render tabs still fall back to the selected location/market when the budget-driven campaign picker source uses a later planning month.
- `COPY_TEMPLATE_PICKER` now presents copy templates with human-readable labels that start with copy angle, then program/topic, persona, offer, and headline preview. The old `PCT-*` / `FCT-*` slots remain hidden backend IDs.
- The README now includes the release gate, allowed/not allowed actions, color legend, team workflow, parent/franchise token rules, import rule, rename rule, n8n phase-1 rule, and `campaign_slot` explanation.
- Color coding is applied: green for safe input, yellow for approval/review, blue for generated/output, red for blockers, gray for source/admin/reference, and purple for n8n/future automation.
- `META_OBJECT_INVENTORY` and `GOOGLE_ADS_OBJECT_INVENTORY` are hidden.
- 56 protected ranges are active for generated, source, import, and admin-managed areas.
- `PARENT_COPY_CW` and `FRANCHISE_COPY_CW` feed the hidden `COPY_TEMPLATE_CW` master tab. Content writers do not manually fill `copy_template_slot` or `copy_template_key`; those fields are generated.
- Meta copy tabs now include optional preview location/market fields so writers can render `{CityName}`, `{SchoolName}`, `{Province}`, `{MarketName}`, `{ProgramName}`, and `{FranchiseTopic}` in the same row before MB selects the final campaign.
- `program_label` is the human-facing label. `program_token` is the generated naming/UTM-safe token and is hidden/protected in user-facing parent tabs.
- Franchise-facing rows use `franchise_topic` and leave parent `program_label` / `program_token` empty in the master output.
- Controlled dropdowns were added or tightened for copy angle, persona, CTA, language, business line, parent program token, franchise topic, offer type, creative visual concept, audience type, placement, destination URL type, aspect ratio, and file type.
- CopyAngle tokens now include the standard writing/naming options `Attention`, `Interest`, `Desire`, `Action`, `Trust`, `Program Fit`, `Curriculum`, `Safety`, `Convenience`, `Social Proof`, `Urgency`, `Diversification`, `Investment`, `Market Opportunity`, `Real Estate`, and `Retargeting`.
- `CAMPAIGN_SELECTOR` now outputs the full budget-driven campaign slot, source, scope, platform, location, generated name, generated key, activation, objective, funnel, theme, month, sequence, and QA fields.
- `CREATIVE_ASSET_REGISTRY_GD` was remapped so master creative rows read final filename, QA status, approval status, owner, and notes from the correct generated/user columns.
- `CREATIVE_ASSET_REGISTRY_GD` was rechecked after adding the first-column location selector; the hidden master formula now keeps platform asset ID columns blank until sync and maps `creative_group_key`, filename, QA, approval, owner, and notes into the correct columns.
- `META_IMPORT_READY` and `GOOGLE_IMPORT_READY` now filter from `BUILD_MANIFEST_MB` using `qa_status=OK`, `approval_status=Approved`, and `PAUSED` status columns.
- A temporary parent LSM Meta POC row for Cornerstone generated a paused Meta import-ready row from the new `month` + `location_or_market` + readable `copy_template_picker` flow, then the test inputs were cleared so final import tabs are empty.
- A temporary franchise render/creative POC row confirmed franchise copy and creative filenames use `franchise_topic`, not parent program tokens, then the test inputs were cleared.
- A temporary Google parent Search/RSA POC row generated a paused `GOOGLE_IMPORT_READY` row with 15 RSA headlines and 4 descriptions, then the test inputs were cleared so final import tabs are empty.
- Final readback found no `ACTIVE` status in the checked Meta/Google import outputs.
- On 2026-05-07, review logic was changed from build-manifest-only review to copy-first review so copy can be reviewed as soon as it exists in the CW/RSA tabs, even when render/build/creative/import steps are incomplete.
- On 2026-05-07, review was split by platform because Meta and Google need different review fields. `META_STAKEHOLDER_REVIEW` now shows Meta primary text, headline, description, CTA, QA, and approval. `GOOGLE_STAKEHOLDER_REVIEW` now shows Google RSA fields, including 15 headlines, 4 descriptions, paths, QA, and approval. The old `STAKEHOLDER_REVIEW` tab is now an index only.
- For the first POC, copy review uses direct copy text from the CW/RSA tabs. Placeholder preview/rendering remains available in hidden/backend columns for future automation but is not required for writer input or stakeholder review. Existing sample rows were converted to literal April/May POC-style copy.
- On 2026-05-07, seven parent LSM Meta copy templates were added to `PARENT_COPY_CW` as draft rows `PCT-005` through `PCT-011`: Attention, Montessori/Curriculum, Nearby/Convenience, New Location, CEFA Baby, Open House, and Summer Camp. These now appear in `META_STAKEHOLDER_REVIEW` and `COPY_TEMPLATE_PICKER`.

`Partial`

- This is an internal POC control surface, not production rollout approval.
- The workbook has not been validated against fresh Meta Ads Manager and Google Ads Editor import templates.
- Destination URL and school/form mapping still depend on `LOCATION_TOKEN_MAP` reconciliation before real import use.
- n8n is not connected yet.
- Platform asset IDs, Meta image hashes, Meta video IDs, Google asset IDs, and YouTube IDs still require upload/export sync before real import use.

`Pending`

- Run the first real POC with one parent LSM destination, one approved copy row, one approved creative row, and one approved paused build row.
- Export fresh Meta Ads Manager and Google Ads Editor templates before any real import.
- Reconcile post-import IDs back into `IMPORT_AUDIT` after the manual platform preview/import.
- Convert the successful POC into n8n phase-1 validation/export/audit workflows.

## Team Workflow

| Team | Primary tab | Edit model |
| --- | --- | --- |
| Content writer - Meta | `PARENT_COPY_CW`, `FRANCHISE_COPY_CW` | Start with `location_or_market`, then fill owner, scope, persona, offer type, copy angle, copy text, CTA, language, and notes. Parent copy uses `program_label`; franchise copy uses `franchise_topic`. Slot/key fields are generated and hidden. |
| Content writer - Google | `GOOGLE_PARENT_RSA_CW`, `GOOGLE_FRANCHISE_RSA_CW` | Start with `location_or_market`, then fill Google-specific RSA copy: up to 15 headlines, 4 descriptions, path fields, copy angle, QA/approval. Do not use the Meta copy tabs for Google RSA copy. |
| Media / MB | `PARENT_RENDER_MB`, `FRANCHISE_RENDER_MB` | Select `month`, `location_or_market`, and the readable `copy_template_picker`, then approve final rendered copy. Campaign keys, hidden slots, rendered copy, and QA fields are generated. |
| Designer | `PARENT_CREATIVE_GD`, `FRANCHISE_CREATIVE_GD` | Start with `location_or_market`, then fill only the practical creative fields: format, concept/ad angle, version, size, file extension, file URL, approval, owner, and notes. Filename/key/QA columns are generated. |
| Media / MB - Meta | `PARENT_BUILD_MB`, `FRANCHISE_BUILD_MB` | Meta-oriented build surfaces. Platform is locked to `META`; use these for Meta campaign/ad set/ad build rows. |
| Media / MB - Google | `GOOGLE_PARENT_BUILD_MB`, `GOOGLE_FRANCHISE_BUILD_MB` | Google-oriented build surfaces. Use these for Google customer/campaign/ad group/asset group/search ad rows and expanded RSA import output. |
| Reviewer - Meta | `META_STAKEHOLDER_REVIEW` | Review Meta copy as soon as it is written in the Meta CW tabs. Build, creative, approval, and import completion are not required for visibility. This tab is not an upload surface. |
| Reviewer - Google | `GOOGLE_STAKEHOLDER_REVIEW` | Review Google RSA copy separately from Meta. This tab includes the Google-specific headline, description, and path fields needed for Search/RSA review. |
| Reviewer index | `STAKEHOLDER_REVIEW` | Index only. Points reviewers to the Meta or Google review tab. |
| Automation / MB | `META_IMPORT_READY`, `GOOGLE_IMPORT_READY`, `IMPORT_AUDIT`, `N8N_PLAN` | Generated/export/audit surfaces only. |

## Frontend / Backend Split

The visible tabs are intended to be the team operating surface:

- `CAMPAIGN_PICKER`
- `PARENT_COPY_CW`
- `FRANCHISE_COPY_CW`
- `PARENT_RENDER_MB`
- `FRANCHISE_RENDER_MB`
- `PARENT_CREATIVE_GD`
- `FRANCHISE_CREATIVE_GD`
- `PARENT_BUILD_MB`
- `FRANCHISE_BUILD_MB`
- `GOOGLE_PARENT_RSA_CW`
- `GOOGLE_FRANCHISE_RSA_CW`
- `GOOGLE_PARENT_BUILD_MB`
- `GOOGLE_FRANCHISE_BUILD_MB`
- `META_STAKEHOLDER_REVIEW`
- `GOOGLE_STAKEHOLDER_REVIEW`
- `STAKEHOLDER_REVIEW`
- `META_IMPORT_READY`
- `GOOGLE_IMPORT_READY`

The hidden tabs are backend consolidation surfaces:

- `COPY_TEMPLATE_CW`
- `COPY_RENDER_MB`
- `CREATIVE_ASSET_REGISTRY_GD`
- `BUILD_MANIFEST_MB`
- `META_OBJECT_INVENTORY`
- `GOOGLE_ADS_OBJECT_INVENTORY`

This keeps the team workflow split by business line while preserving one controlled backend contract for Meta, Google, QA, and future n8n phase-1 automation.

The Google tabs are intentionally separate because Google Search and Google Ads Editor imports need different copy and object fields than Meta:

- Customer ID
- Campaign ID
- Ad group ID
- Asset group ID
- Search/PMax campaign type
- Keyword theme
- Match strategy
- 15 RSA headlines
- 4 RSA descriptions
- Path 1 and Path 2
- Google-specific final URL suffix / UTM output

## Guardrails

- Do not use this sheet for live activation, live budget edits, live renames, deletion, bid strategy changes, optimization-event changes, pixel changes, or conversion-goal changes.
- Budget tabs are read-only references from the OneDrive/SharePoint budget workbook. They are not approved platform budget instructions.
- Parent rows use `program_token`; franchise rows use `franchise_topic` and `offer_type`.
- Do not manually type final campaign, ad set, ad group, ad, creative filename, or UTM keys where formulas generate them.
- Existing platform objects must be handled by ID, not by name-only matching.
- Import/API-created platform objects must default to `PAUSED`.
- `CAMPAIGN_RENAME_REVIEW` is review-only until CEFA approves a separate ID-backed rename batch.
- For the April/May 2026 POC, keep visible month dropdowns limited to `2026-04` and `2026-05` until CEFA approves a wider rollout window.
- For the April/May 2026 POC, write direct location/program-specific copy in the CW/RSA tabs. Do not require `{CityName}`, `{ProgramName}`, or other placeholder rendering for stakeholder review.
