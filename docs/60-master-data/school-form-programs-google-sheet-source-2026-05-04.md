# School Form Programs Google Sheet Source

Last updated: 2026-05-04

## Scope

| Field | Value |
| --- | --- |
| Workstream | `docs/60-master-data/` |
| Source type | Google Sheet reference |
| Sheet title | `CEFA School Form Programs` |
| Sheet URL | [CEFA School Form Programs](https://docs.google.com/spreadsheets/d/1CFWM84XT0NGTlaJkg5NjUxCjQZMnxd0Fy5G6SfdPACc/edit?usp=sharing) |
| Spreadsheet ID | `1CFWM84XT0NGTlaJkg5NjUxCjQZMnxd0Fy5G6SfdPACc` |
| Tab checked | `Programs shown on form` |
| Live writes made | No |

## Why This Belongs Here

This sheet contains school-level parent-form reference data: school URLs, parent inquiry form URLs, school slugs, numeric school IDs, and programs shown on each parent inquiry form.

It is master data first. Naming-convention work can use it as an input for parent `ProgramTag` dropdowns and campaign/location validation, but the sheet does not itself define Meta campaign naming, UTM rules, conversion events, or budget decisions.

## Checked Structure

`Verified`

- The spreadsheet is readable with Google Sheets access.
- It has one checked tab: `Programs shown on form`.
- The tab has 9 columns and 51 data rows.

Columns:

| Column | Status | Notes |
| --- | --- | --- |
| `School Name` | `Partial` | Human-readable school label. |
| `School City` | `Partial` | Some rows contain multiple cities. |
| `School Region` | `Partial` | Region label for school grouping. |
| `School URL` | `Partial` | Parent school page URL. |
| `Programs Shown on Parent Inquiry Form` | `Partial` | Program labels shown for the school inquiry form. |
| `Program Count` | `Partial` | Count of program labels in the program field. |
| `Inquiry Form URL` | `Partial` | Parent inquiry form URL with `location={school_slug}`. |
| `School Slug` | `Partial` | Location slug used in URLs and form query parameters. |
| `School ID` | `Partial` | Numeric school ID from the sheet; exact system ownership still needs confirmation. |

## Program Coverage Observed

`Partial`

- 50 of 51 rows show 4 programs.
- 1 row, `calgary-cornerstone`, shows 5 programs because it includes `CEFA Weekend Care Program`.
- The same 4 parent programs appear in different orders across rows: `CEFA Baby`, `Junior Kindergarten 1`, `Junior Kindergarten 2`, and `Junior Kindergarten 3`.

For naming-convention work, normalize these to controlled tokens rather than using raw display order from the sheet:

| Display label | Suggested token |
| --- | --- |
| `ALL` | `all` |
| `CEFA Baby` | `cefa_baby` |
| `Junior Kindergarten 1` | `jk1` |
| `Junior Kindergarten 2` | `jk2` |
| `Junior Kindergarten 3` | `jk3` |
| `CEFA Weekend Care Program` | `weekend_care` |

## Reconciliation Against BigQuery School Dimension

Checked against `marketing-api-488017.mart_marketing.dim_school` on 2026-05-04.

`Partial`

- Google Sheet rows checked: 51
- BigQuery `dim_school` rows checked: 53
- The sheet is useful but should not replace `dim_school` until these differences are resolved.

Slugs in BigQuery but not in the sheet:

| BigQuery slug | BigQuery location name | Status |
| --- | --- | --- |
| `langley-city-center` | `Langley - City Center` | `Open question` |
| `south-surrey-morgan-crossing-east` | `South Surrey - Morgan Crossing East` | `Open question` |
| `surrey-panorama` | `Surrey - Panorama` | `Open question` |
| `surrey-panorama-north` | `Surrey - Panorama North` | `Open question` |
| `ubc` | `UBC` | `Open question` |

Slugs in the sheet but not in BigQuery:

| Sheet slug | Sheet school name | Status |
| --- | --- | --- |
| `langley-city-centre` | `Langley - City Centre` | `Open question` |
| `south-surrey-panorama` | `South Surrey - Panorama` | `Open question` |
| `vancouver-ubc` | `Vancouver - UBC` | `Open question` |

Label differences on shared slugs:

| Slug | Sheet label | BigQuery label | Status |
| --- | --- | --- | --- |
| `calgary-south` | `Calgary South` | `Calgary - South` | `Partial` |
| `delta-captains-cove` | `Delta - Captain's Cove` | `Delta - Captains Cove` | `Partial` |
| `new-westminster-downtown` | `New Westminster - Downtown` | `New Westminster Downtown` | `Partial` |
| `new-westminster-uptown` | `New Westminster - Uptown` | `New Westminster Uptown` | `Partial` |
| `okotoks-darcy-crossing` | `Okotoks - D'Arcy Crossing` | `Okotoks - Darcy Crossing` | `Partial` |

## Recommended Use

- Use this sheet as a governed reference for parent school URL, inquiry form URL, parent program availability, and source school IDs.
- Use `dim_school.school_uuid` as the parent tracking join key unless a future verified source changes that decision.
- Use `School Slug` only as an alias until reconciled against `dim_school` and live WordPress/School Manager.
- Use the program field to inform parent naming-convention `ProgramTag` dropdowns, but normalize program tokens before writing campaign/ad/copy/creative names.

## Open Questions

- Confirm which system owns the numeric `School ID` values.
- Confirm whether the sheet intentionally excludes South Surrey - Morgan Crossing East and Surrey - Panorama North.
- Confirm whether `langley-city-centre` or `langley-city-center` is the canonical production slug.
- Confirm whether `vancouver-ubc` or `ubc` is the canonical production slug.
- Confirm whether `south-surrey-panorama` should map to `surrey-panorama` in `dim_school`.
