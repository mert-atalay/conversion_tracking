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
- Use proposed `campaign_key`, `ad_set_key`, and `ad_data_key` for future UTMs only after the row is reviewed and approved.
- Do not backfill historical reporting by name alone.
- Do not use `needs_review` ad-level proposed names for final creative naming until the creative/copy source is checked.

## Live Change Boundary

`Pending`

- No live campaign, ad set, ad, budget, status, or conversion-setting changes were made.
- Before any live Meta rename, export the affected rows from the CSV, review `current_name -> proposed_nc2_name`, and get explicit approval.
