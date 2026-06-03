# Meta Naming NC2 Active Last-30 Inventory

Last updated: 2026-05-04

## Scope

| Field | Value |
| --- | --- |
| Workstream | `docs/40-naming-convention/` |
| Platform | Meta Ads |
| Accounts checked | `parent` / CEFA Early Learning, `franchise` / CEFA Franchisor |
| Delivery window | `2026-04-05` through `2026-05-04` |
| Source | Repo-local CEFA Meta CLI, `tools/meta/cefa-meta` |
| Live Meta writes made | No |
| Inventory CSV | [`data/reference/cefa-meta-active-object-inventory-2026-04-05-to-2026-05-04.csv`](../../data/reference/cefa-meta-active-object-inventory-2026-04-05-to-2026-05-04.csv) |

## Status

`Verified`

- Meta API reads worked through the repo-local CLI.
- Last-30-day campaign, ad set, and ad delivery rows were pulled from Meta insights.
- Current object metadata was joined back to the delivered object IDs.
- The inventory CSV includes actual campaign, ad set, and ad names and IDs.

`Partial`

- Proposed `NC2` names in the CSV are planning names, not live Meta renames.
- Some ad-level proposals are inferred from incomplete visible ad names and are marked `needs_review`.
- Program tags for parent ads default to `ALL Programs` unless the current name or filename clearly exposes a narrower program token.

## Final NC2 Structure

Use this structure for proposed new names, rename planning, workbook generation, UTMs, and conversion-tracking joins.

Campaign:

```text
CEFA | {BudgetScope} | {Activation} | {LocationOrGroup} | META | {Objective} | {Funnel} | {Theme} | {YYYYMM} | {Seq}
```

Ad set:

```text
{Persona} | {AudienceType} | {Geo} | {Placement}
```

Ad:

```text
{FormatTag} | {ProgramOrTopic} | {VisualConcept} | {CopyAngle} | v{AdVersion}
```

UTM contract:

```text
utm_source=meta
utm_medium=paid_social
utm_campaign={campaign_key}
utm_content={ad_data_key}
utm_term={ad_set_key}
```

## Required Join Fields

Use IDs as the stable source of truth for historical joins. Names can change.

| Level | Required ID | Naming key |
| --- | --- | --- |
| Account | `account_id` | `account_alias` |
| Campaign | `campaign_id` | `campaign_key` / CSV `proposed_key` when `object_level=campaign` |
| Ad set | `adset_id` | `ad_set_key` / CSV `proposed_key` when `object_level=ad_set` |
| Ad | `ad_id` | `ad_data_key` / CSV `proposed_key` when `object_level=ad` |

## ID Inventory Contract

`Verified`

The inventory CSV is the current GitHub-backed ID crosswalk for Meta rename planning. Use it as the object handle list before any future live rename, bulk upload, n8n workflow, QA export, or conversion-tracking join.

| CSV field | Campaign rows | Ad set rows | Ad rows |
| --- | --- | --- | --- |
| `object_level` | `campaign` | `ad_set` | `ad` |
| `object_id` | Campaign ID | Ad set ID | Ad ID |
| `current_name` | Current campaign name | Current ad set name | Current ad name |
| `parent_campaign_id` | Same campaign ID | Parent campaign ID | Parent campaign ID |
| `parent_campaign_name` | Same campaign name | Parent campaign name | Parent campaign name |
| `parent_adset_id` | Blank | Same ad set ID | Parent ad set ID |
| `parent_adset_name` | Blank | Same ad set name | Parent ad set name |
| `proposed_nc2_name` | Proposed campaign name | Proposed ad set name | Proposed ad name |
| `proposed_key` | Proposed `campaign_key` | Proposed `ad_set_key` | Proposed `ad_data_key` |
| `naming_status` | Rename-planning status | Rename-planning status | Rename-planning status |

Practical rule: never identify a live object for renaming by name alone. Filter or import by the matching ID column first, then compare `current_name -> proposed_nc2_name`.

## Rename Workflow Guardrail

`Pending`

No live Meta rename has been approved yet. When CEFA is ready to rename objects:

1. Export the affected rows from the inventory CSV by `account_alias` and `object_level`.
2. Review `object_id`, `current_name`, `proposed_nc2_name`, `proposed_key`, and `naming_status`.
3. Do not rename rows marked `needs_review` until the underlying creative/copy source is checked.
4. Build any Meta bulk sheet, n8n job, or API request with IDs included:
   - Campaign rename rows must include `campaign_id`.
   - Ad set rename rows must include `adset_id` and `parent_campaign_id`.
   - Ad rename rows must include `ad_id`, `parent_adset_id`, and `parent_campaign_id`.
5. Keep an export of the approved `old_name -> new_name` mapping with IDs before changing anything live.

## Inventory Summary

`Verified`

| Account | Campaigns | Ad sets | Ads |
| --- | ---: | ---: | ---: |
| CEFA Early Learning / `parent` | 21 | 31 | 133 |
| CEFA Franchisor / `franchise` | 4 | 9 | 64 |

`Partial`

- Campaign-level proposed names are complete for all 25 delivered campaigns.
- Ad set proposed names are complete for all 40 delivered ad sets.
- Ad-level proposed names include 45 `needs_review` rows because the current ad name does not expose enough format, concept, or copy-angle detail.

## Active Campaign Findings

`Verified`

- Parent active/delivered campaign naming is mixed. Some campaigns are close to NC1, while others use short names such as `beltline | LSM | conversions (updated)`, `capilano | LSM | conversion | daily`, and `Victoria Heights | LSM | prospecting | lifetime`.
- Franchise active/delivered campaign naming is not aligned to the parent structure. Current examples include `cefa franchise | ontario | prospecting`, `Reshift Franchise Acquisition - US New`, and `USA |  Chicago | National | Tradeshow`.
- Meta platform objective can disagree with the visible campaign name. For example, a campaign name can contain `AWARENESS` or `ENGAGEMENT` while the platform objective read from Meta is different. The NC2 proposed campaign names use the platform objective token because conversion reporting should map to what Meta is actually optimizing against.

## Conversion Tracking Use

Use the inventory CSV as the active Meta object crosswalk for the current transition:

- Keep `campaign_id`, `adset_id`, and `ad_id` in all conversion-tracking exports and QA tables.
- Keep `parent_campaign_id` and `parent_adset_id` on ad-level rows so conversions can be reconciled across account, campaign, ad set, and ad dimensions after names change.
- Use these IDs as destination fields in the [Meta creative build import manifest contract](./meta-creative-build-import-manifest-2026-05-04.md) before creating or updating ads from new CEFA creatives.
- Use proposed `campaign_key`, `ad_set_key`, and `ad_data_key` for future UTMs only after the row is reviewed and approved.
- Store old/current names and proposed names as labels, not primary join keys.
- Do not backfill historical reporting by name alone.
- Do not use `needs_review` ad-level proposed names for final creative naming until the creative/copy source is checked.

## Live Change Boundary

`Pending`

- No live campaign, ad set, ad, budget, status, or conversion-setting changes were made.
- Before any live Meta rename, export the affected rows from the CSV, review `current_name -> proposed_nc2_name`, and get explicit approval.
