# Paid Media Build Control Center v21 Final POC

Last updated: 2026-05-06

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
- The workbook has the v21 tabs for settings, location mapping, budget references, campaign selector, content copy, rendered copy, creative assets, carousel cards, build manifest, stakeholder review, Meta import output, Google import output, rename review, pixel/event QA, n8n plan, object destinations, import audit, QA report, and raw inventories.
- The README now includes the release gate, allowed/not allowed actions, color legend, team workflow, parent/franchise token rules, import rule, rename rule, n8n phase-1 rule, and `campaign_slot` explanation.
- Color coding is applied: green for safe input, yellow for approval/review, blue for generated/output, red for blockers, gray for source/admin/reference, and purple for n8n/future automation.
- `META_OBJECT_INVENTORY` and `GOOGLE_ADS_OBJECT_INVENTORY` are hidden.
- 34 protected ranges are active for generated, source, import, and admin-managed areas.
- `COPY_TEMPLATE_CW` now generates `copy_template_slot` and `copy_template_key`; content writers do not manually fill those fields.
- Controlled dropdowns were added or tightened for copy angle, persona, CTA, language, business line, parent program token, franchise topic, offer type, creative visual concept, audience type, placement, destination URL type, aspect ratio, and file type.
- `CAMPAIGN_SELECTOR` now outputs the full budget-driven campaign slot, source, scope, platform, location, generated name, generated key, activation, objective, funnel, theme, month, sequence, and QA fields.
- `META_IMPORT_READY` and `GOOGLE_IMPORT_READY` now filter from `BUILD_MANIFEST_MB` using `qa_status=OK`, `approval_status=Approved`, and `PAUSED` status columns.
- A temporary parent LSM Meta POC row for Cornerstone generated a paused Meta import-ready row, then the test inputs were cleared so final import tabs are empty.
- Final readback found no `ACTIVE` status in the checked Meta/Google import outputs.

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
| Content writer | `COPY_TEMPLATE_CW` | Fill owner, platform, scope, business line, persona, parent program or franchise topic, offer type, copy angle, copy text, CTA, language, and notes. `copy_template_slot`, `copy_template_key`, and QA columns are generated/protected. |
| Media / MB | `COPY_RENDER_MB` | Select campaign slot and copy template, approve final rendered copy. Rendered copy fields are generated. |
| Designer | `CREATIVE_ASSET_REGISTRY_GD` | Fill creative metadata, format, concept, file link, and asset notes. Filename/key/QA columns are generated. |
| Media / MB | `BUILD_MANIFEST_MB` | Select campaign slot, platform, IDs, copy, creative, destination type, approval, and publish status. Generated keys, UTMs, names, and statuses are protected. |
| Reviewer | `STAKEHOLDER_REVIEW` | Review generated build rows only. This tab is not an upload surface. |
| Automation / MB | `META_IMPORT_READY`, `GOOGLE_IMPORT_READY`, `IMPORT_AUDIT`, `N8N_PLAN` | Generated/export/audit surfaces only. |

## Guardrails

- Do not use this sheet for live activation, live budget edits, live renames, deletion, bid strategy changes, optimization-event changes, pixel changes, or conversion-goal changes.
- Budget tabs are read-only references from the OneDrive/SharePoint budget workbook. They are not approved platform budget instructions.
- Parent rows use `program_token`; franchise rows use `franchise_topic` and `offer_type`.
- Do not manually type final campaign, ad set, ad group, ad, creative filename, or UTM keys where formulas generate them.
- Existing platform objects must be handled by ID, not by name-only matching.
- Import/API-created platform objects must default to `PAUSED`.
- `CAMPAIGN_RENAME_REVIEW` is review-only until CEFA approves a separate ID-backed rename batch.
