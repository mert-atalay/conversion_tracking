# Budget-Driven Meta Naming v20 Final-v3 Review

Last updated: 2026-05-04

## Scope

| Field | Value |
| --- | --- |
| Workstream | `docs/40-naming-convention/` |
| Platform | Meta Ads naming, dynamic copy, and bulk import prep |
| Drive folder | [final v3](https://drive.google.com/drive/folders/1OYm5c2hA7UZF3AXk5XvOvIcMq6g-P_qN) |
| Workbook | [CEFA_Budget_Driven_Meta_Naming_Bulk_Builder_v20_DYNAMIC_COPY.xlsx](https://docs.google.com/spreadsheets/d/1A2WmOmADovTHV69zt9kA5KtBWoatAJOD/edit?usp=drivesdk&ouid=100264075182330360487&rtpof=true&sd=true) |
| Workflow note | [CEFA_v20_Dynamic_Copy_Template_Workflow_and_n8n_Plan.md](https://drive.google.com/file/d/1e5EsasmJBOiIDQkuefQI79JbFdI35tMe/view?usp=drivesdk) |
| Live writes made | No |

## Review Status

`Verified`

- The final-v3 Drive folder exists and contains the v20 dynamic-copy workbook plus a workflow/n8n markdown plan.
- The workbook has 23 sheets, including `LOCATION_TOKEN_MAP`, `COPY_INPUT_CW`, `COPY_RENDER_MB`, `META_AD_BUILD_MB`, `META_IMPORT_READY`, `NAMING_STANDARD`, `N8N_PLAN`, and `SOURCES`.
- `META_IMPORT_READY` campaign, ad set, and ad statuses default to `PAUSED`.
- The plan correctly separates parent program tags from franchise topics/offers.
- The plan correctly requires rendered final copy before Meta import and blocks unresolved placeholders conceptually.

`Partial`

- The workbook is a strong structural draft but is not ready as the governed source of truth.
- Several sample rows are hardcoded, while new workflow rows depend on formulas that do not currently generate campaign names/keys correctly.

## What To Preserve

- Dynamic copy template workflow: CW writes reusable templates in `COPY_INPUT_CW`, then MB renders campaign-specific copy in `COPY_RENDER_MB`.
- Parent vs franchise separation: parent campaigns use parent program tags; franchise campaigns use franchise topic/offer tags.
- `LOCATION_TOKEN_MAP` concept for `{CityName}`, `{SchoolName}`, `{Province}`, `{MarketName}`, `{ProgramName}`, `{FranchiseTopic}`, and `{LocationSlug}`.
- `META_IMPORT_READY` statuses defaulting to `PAUSED`.
- n8n phase-1 boundary: validate, render, generate import file, sync IDs, sync assets, and report only. No direct launch, activation, budget change, deletion, or optimization-setting changes.

## Blocking Fixes Before Team Rollout

`Open question / needs fix`

1. Budget-tab campaign-name/key formulas are in the wrong columns.
   - In `BUDGET_LSM`, `BUDGET_CORP`, and `BUDGET_FRANCHISE`, column `AM` is labeled `Activation` but contains the campaign-name formula.
   - Column `AN` is labeled `Objective` but contains the campaign-key formula.
   - The intended auto columns `AR` (`Campaign Name (auto)`) and `AS` (`Campaign Key (auto)`) are blank.
   - The formula in `AM` also references `$AM` and `$AN`, creating a circular/self-referential logic problem.
   - Downstream `CAMPAIGN_SELECTOR` formulas expect the campaign name/key in `AR`/`AS`, so new media-plan rows will not flow correctly.

2. Dropdown/data validation is incomplete.
   - `COPY_INPUT_CW` has some dropdown validation.
   - `BUDGET_LSM`, `BUDGET_CORP`, `BUDGET_FRANCHISE`, `CREATIVE_INPUT_GD`, and `META_AD_BUILD_MB` do not have dropdown validations in the checked file.
   - This is risky for non-technical users because token spelling drives campaign keys and reporting joins.

3. `LOCATION_TOKEN_MAP` is not reconciled to the governed school/form source.
   - The final-v3 workbook has 31 token-map rows.
   - The governed school form programs sheet has 51 school rows, and BigQuery `dim_school` has 53 rows.
   - Many parent landing URLs in v20 still use `/cefa-find-a-school/`, while the school/form source uses `/school/{school_slug}/` plus inquiry URLs at `/submit-an-inquiry-today/?location={school_slug}`.
   - The workbook should separate `School URL` and `Inquiry Form URL` instead of using one generic `Landing URL`.

4. UTM builder/output columns are missing from the import flow.
   - `NAMING_STANDARD` defines `utm_campaign={campaign_key}` and `utm_content={ad_data_key}`.
   - `META_IMPORT_READY` does not expose a final `URL Tags` column or separate `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, and `utm_term` fields.
   - The workbook should generate URL tags from stable keys, not from Meta dynamic names.

5. Current-campaign rename table is missing.
   - The workbook does not include the current campaign-name normalization table requested for campaigns such as `Victoria Heights | LSM | prospecting | lifetime`, `Reshift Franchise Acquisition - US New`, `New Leads campaign`, and `New Sales campaign`.
   - Keep the rename table separate from the import-ready table so historical cleanup does not accidentally become a new campaign import.

6. Parent program tags need display-label and machine-token separation.
   - The workbook uses labels like `ALL Programs` in ad names and keys.
   - Recommended machine tokens are `all`, `cefa_baby`, `jk1`, `jk2`, `jk3`, and approved combinations.
   - Keep user-facing display labels separate from reporting-safe tokens.

7. Placeholder QA needs to validate approved placeholders, not only brace balance.
   - `COPY_INPUT_CW` checks `{` and `}` balance.
   - It should also flag unsupported placeholders such as `{School}` or `{Town}` even if braces are balanced.

8. Copy length QA is not propagated to import QA.
   - `COPY_RENDER_MB` can flag `HEADLINE_LONG`, `DESCRIPTION_LONG`, or `PRIMARY_TEXT_LONG`.
   - `META_AD_BUILD_MB` / `META_IMPORT_READY` can still show `OK` if required fields and placeholders are present.
   - Length warnings should be visible in stakeholder review and import QA.

## Recommended Fix Pattern

- Keep `AM:AQ` as user/dropdown fields: `Activation`, `Objective`, `Funnel`, `Theme`, `Seq`.
- Put campaign-name formula in `AR`.
- Put campaign-key formula in `AS`.
- Make `CAMPAIGN_SELECTOR` read only from `AR`/`AS`.
- Add dropdown validation to all user-entry token columns.
- Replace or extend `LOCATION_TOKEN_MAP` from the governed school form programs source and BigQuery school dimension reconciliation.
- Add explicit URL fields:
  - `School URL`
  - `Inquiry Form URL`
  - `Destination URL Type`
  - `Final Destination URL`
  - `URL Tags`
- Add UTM fields:
  - `utm_source=meta`
  - `utm_medium=paid_social`
  - `utm_campaign={campaign_key}`
  - `utm_content={ad_data_key}`
  - `utm_term={ad_set_key_or_ad_set_id}`

## Current Recommendation

Do not share final v3/v20 as the team source of truth yet.

Use it as the best current structural draft because the dynamic-copy direction is right. Fix the formula placement, dropdown validation, URL/UTM output, location/form URL mapping, and campaign rename table first. After those fixes, it can become the candidate `NC2` workbook.
