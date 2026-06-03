# Paid Media Build Control Center POC

Last updated: 2026-05-05

## Scope

| Field | Value |
| --- | --- |
| Workstream | `docs/40-naming-convention/` |
| Platform scope | Meta Ads and Google Ads build/naming workflow |
| Google Sheet | [CEFA Paid Media Build Control Center - POC v1 - 2026-05-05](https://docs.google.com/spreadsheets/d/11mlcPQy_nz-XvjgSotl0cCWAJr2BS8REK6Ex2nOIMYI/edit) |
| Drive folder | [final v3](https://drive.google.com/drive/folders/1OYm5c2hA7UZF3AXk5XvOvIcMq6g-P_qN) |
| Created with | Personal Google CLI / API under `yigitmertatalay@gmail.com` |
| Live platform writes made | No |

## Status

`Verified`

- A native Google Sheet was created in the final-v3 Drive folder.
- The sheet has 14 tabs, including team-entry tabs, admin/build tabs, generated QA/import tabs, settings, naming standards, and hidden source inventory tabs.
- The sheet readback confirms `META_OBJECT_INVENTORY` and `GOOGLE_ADS_OBJECT_INVENTORY` are hidden.
- The sheet has warning-only protected ranges for generated/admin-managed areas and formula columns.
- `BUDGET_SYNC` was populated from the canonical OneDrive budget workbook's budget sections.
- `OBJECT_DESTINATIONS` was populated from the GitHub-backed Meta and Google Ads active object inventories.
- No Meta Ads or Google Ads live object, budget, bidding, status, tracking-template, or conversion-action changes were made.

`Partial`

- This is a POC control surface, not the final production workbook.
- The first row is a blocked sample row to show QA behavior; it is not an import-ready row.
- `IMPORT_READY` only fills when a `BUILD_MANIFEST` row passes QA and has `approval_status=Approved`.
- The sheet has not yet been connected to n8n automation.
- Destination URL reconciliation against the governed school/form URL source still needs to be completed before real import use.

`Pending`

- Run a real small POC with one parent LSM destination, one copy row, one creative row, and one approved paused build row.
- Convert successful POC behavior into n8n validation/export workflows.
- Decide whether this sheet replaces, extends, or feeds the existing v20 workbook after the POC.

## Sheet Structure

| Tab | Role | Edit model |
| --- | --- | --- |
| `README` | Human operating guide and guardrails | Read-only/reference |
| `TEAM_INTAKE` | Simple intake surface for requested creative/copy builds | Team editable, formula columns protected with warning |
| `COPY_LIBRARY` | Content team's primary text, headline, description, CTA, and copy keys | Team editable, generated key/QA columns protected with warning |
| `CREATIVE_ASSET_REGISTRY` | Creative team's file links, format, concept, program, version, and suggested filename | Team editable, generated key/QA columns protected with warning |
| `BUDGET_SYNC` | Budget reference from the canonical budget workbook | Admin/generated |
| `OBJECT_DESTINATIONS` | Unified Meta/Google destination keys and IDs | Admin/generated |
| `BUILD_MANIFEST` | MB/build-owner mapping from copy + creative + destination + budget context | Admin/build-owner editable, generated columns protected with warning |
| `IMPORT_READY` | Generated approved rows only | Generated |
| `QA_REPORT` | Generated blockers and warnings | Generated |
| `IMPORT_AUDIT` | Future n8n/import result log | Admin/generated |
| `SETTINGS` | Controlled dropdown values | Admin |
| `NAMING_STANDARD` | Compact rule reference | Reference |
| `META_OBJECT_INVENTORY` | Raw GitHub-backed Meta inventory mirror | Hidden/generated |
| `GOOGLE_ADS_OBJECT_INVENTORY` | Raw GitHub-backed Google Ads inventory mirror | Hidden/generated |

## Guardrails

- Creative/content users should not manually type final campaign, ad set, ad group, or ad names.
- Users should fill controlled fields, copy, creative metadata, URLs, and notes; generated formulas create keys/names/UTMs/QA status.
- Budget values are planning/reference only. Do not push live platform budget changes from the sheet without a separate explicit approval.
- Import/API-created platform objects must default to `PAUSED`.
- Existing platform objects must be selected by ID-backed destination keys from `OBJECT_DESTINATIONS`, not by name-only matching.

## Next POC Step

Use one parent LSM location as the first real build test:

1. Add one approved copy row in `COPY_LIBRARY`.
2. Add one approved creative row in `CREATIVE_ASSET_REGISTRY`.
3. Select the ID-backed destination in `BUILD_MANIFEST`.
4. Add the final destination URL.
5. Confirm `QA_REPORT` clears and `IMPORT_READY` produces one paused approved row.
6. Only then generate a Meta/Google import file or n8n validation output.
