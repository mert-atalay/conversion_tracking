# Google Ads Naming GADS1 Active Last-30 Inventory

Last updated: 2026-05-04

## Scope

| Field | Value |
| --- | --- |
| Workstream | `docs/40-naming-convention/` |
| Platform | Google Ads |
| Accounts checked | `parent` / CEFA $3000, `franchise` / CEFA Franchisor |
| Delivery window | `2026-04-05` through `2026-05-04` |
| Source | Google Ads API v20 through local protected CEFA Google Ads config |
| Live Google Ads writes made | No |
| Inventory CSV | [`data/reference/cefa-google-ads-active-object-inventory-2026-04-05-to-2026-05-04.csv`](../../data/reference/cefa-google-ads-active-object-inventory-2026-04-05-to-2026-05-04.csv) |

## Status

`Verified`

- Google Ads API access worked for the CEFA manager login customer and the two checked child accounts.
- Campaign, ad group, ad, and Performance Max asset group delivery rows were pulled from Google Ads for the 2026-04-05 through 2026-05-04 delivery window.
- The inventory CSV includes current names and IDs for campaign, ad group, asset group, and ad rows where those objects delivered impressions, clicks, or spend in the checked window.
- No live Google Ads rename, budget, bidding, conversion-action, status, or asset changes were made.

`Partial`

- Proposed `GADS1` names are planning names, not live Google Ads renames.
- Google Ads ads do not have a normal human-visible ad name field like Meta ads, so ad rows use `ad_id` plus a build key rather than a proposed live ad name.
- Several ad group names are inferred from current keyword-theme wording and should be reviewed before any live rename.
- The franchise Performance Max campaign currently contains `traffic` in the name, but the proposed name treats it as lead/franchise-acquisition work because the current name also references application submit. This row is marked `needs_review`.

## Proposed GADS1 Structure

Use this structure for Google Ads rename planning, workbook generation, UTMs, and conversion-tracking joins.

Campaign:

```text
CEFA | {BudgetScope} | {Activation} | {LocationOrGroup} | GOOGLE | {Channel} | {Objective} | {Funnel} | {Theme} | {YYYYMM} | {Seq}
```

Search ad group:

```text
{PersonaOrIntent} | {KeywordTheme} | {GeoOrMarket} | {MatchStrategy}
```

Performance Max asset group:

```text
Asset Group | {GeoOrMarket} | PMax
```

Google ad build key:

```text
{campaign_key}__{ad_group_or_asset_group_key}__{copy_angle_slug}__ad-v{#}__gads1
```

UTM contract:

```text
utm_source=google
utm_medium=cpc
utm_campaign={campaign_key}
utm_content={ad_build_key}
utm_term={keyword_or_ad_group_key}
```

Google Ads auto-tagging and `gclid` should stay enabled where currently used. UTMs are a fallback/reporting contract and should not replace `gclid`.

## Required Join Fields

Use IDs as the stable source of truth for historical joins. Names can change.

| Level | Required ID | Naming key |
| --- | --- | --- |
| Account | `customer_id` | `account_alias` |
| Campaign | `campaign_id` / CSV `object_id` when `object_level=campaign` | `campaign_key` / CSV `proposed_key` |
| Search ad group | `ad_group_id` / CSV `object_id` when `object_level=ad_group` | `ad_group_key` / CSV `proposed_key` |
| Performance Max asset group | `asset_group_id` / CSV `object_id` when `object_level=asset_group` | `asset_group_key` / CSV `proposed_key` |
| Ad | `ad_id` / CSV `object_id` when `object_level=ad` | `ad_build_key` / CSV `proposed_key` |

## Inventory Summary

`Verified`

| Account | Campaigns | Search ad groups | PMax asset groups | Ads |
| --- | ---: | ---: | ---: | ---: |
| CEFA $3000 / `parent` | 19 | 76 | 3 | 97 |
| CEFA Franchisor / `franchise` | 3 | 9 | 1 | 13 |

`Verified`

Campaign spend in the checked delivery window:

| Account | Campaign spend |
| --- | ---: |
| CEFA $3000 / `parent` | `$16,240.04` |
| CEFA Franchisor / `franchise` | `$2,358.30` |

## Active Campaign Naming Findings

`Verified`

- Parent Google Ads campaign names are mixed-format. LSM search campaigns currently use short names such as `oakville | lsm | kw`, `Kelowna Spall | LSM | Conversions`, and `campbell heights | LSM | Keywords`.
- Parent corporate Performance Max campaigns are closer to a structured format but still need the standard `GOOGLE` platform token and consistent location/group placement.
- The parent branded search campaign is active in the delivery window as `corp | search | branded | cefa | always on`.
- Franchise Google Ads campaign names are short-format, for example `franch | search | kw | ontario`, `franch | search | kw | alberta`, and `fr | traffic | application submit`.
- Search ad groups are mostly keyword-theme based, but their naming style varies by location and legacy build style.
- Several delivered parent ads are older `EXPANDED_TEXT_AD` objects. They should be treated as ID-only historical/live objects, not as a reusable naming pattern for new build rows.

## Example Campaign Rename Planning Rows

`Partial`

These are planning examples from the inventory CSV. They are not live rename approval.

| Account | Current campaign name | Proposed GADS1 campaign name |
| --- | --- | --- |
| Parent | `oakville | lsm | kw` | `CEFA | LSM | Enrollment | Oakville | GOOGLE | SEARCH | LEADS | BOF | Enrollment | 202604 | 001` |
| Parent | `Kelowna Spall | LSM | Conversions` | `CEFA | LSM | Enrollment | Kelowna Spall | GOOGLE | SEARCH | LEADS | BOF | Enrollment | 202604 | 001` |
| Parent | `Surrey Panorama | LSM | Conversion` | `CEFA | LSM | Enrollment | South Surrey - Panorama | GOOGLE | SEARCH | LEADS | BOF | Enrollment | 202604 | 001` |
| Parent | `CEFA | BC | CORP | PMAX | LEADS | MOF | Enrollment` | `CEFA | CORP | Enrollment | British Columbia | GOOGLE | PMAX | LEADS | MOF | Enrollment | 202604 | 001` |
| Parent | `corp | search | branded | cefa | always on` | `CEFA | CORP | Brand | All Locations | GOOGLE | SEARCH | LEADS | BOF | Brand | 202604 | 001` |
| Franchise | `franch | search | kw | ontario` | `CEFA | FRANCHISE | FranchiseAcq | Ontario | GOOGLE | SEARCH | LEADS | BOF | FranchiseAcq | 202604 | 001` |
| Franchise | `fr | traffic | application submit` | `CEFA | FRANCHISE | FranchiseAcq | Canada | GOOGLE | PMAX | LEADS | MOF | FranchiseAcq | 202604 | 001` |

## Google Ads Build And Bulk Guardrails

`Pending`

Google Ads bulk work should use a Google-specific build manifest, not the Meta import manifest directly.

Minimum Google Ads build row requirements:

- `account_alias` and `customer_id`;
- `campaign_id` and `campaign_key`;
- `ad_group_id` and `ad_group_key` for Search rows;
- `asset_group_id` and `asset_group_key` for Performance Max rows;
- `ad_id` only when updating an existing ad;
- `budget_group`, `location_name`, and `location_slug` where applicable;
- `keyword_theme`, `match_strategy`, `program_token`, or `franchise_topic`;
- final URL, final URL suffix / tracking template inputs, and generated UTM fields;
- RSA headline and description fields for Search ad builds;
- PMax asset references for PMax builds;
- `qa_status`, `approval_status`, and `publish_status`;
- default new campaign, ad group, asset group, and ad status of `PAUSED` unless explicitly approved.

## Rename Workflow Guardrail

`Pending`

No live Google Ads rename has been approved yet. When CEFA is ready to rename Google Ads objects:

1. Export affected rows from the inventory CSV by `account_alias` and `object_level`.
2. Review `object_id`, `current_name`, `proposed_gads_name`, `proposed_key`, and `naming_status`.
3. Do not rename rows marked `needs_review` until the underlying campaign objective or object purpose is confirmed.
4. Build any bulk sheet, n8n job, or API request with IDs included:
   - Campaign rename rows must include `campaign_id`.
   - Search ad group rename rows must include `ad_group_id` and `parent_campaign_id`.
   - Performance Max asset group rename rows must include `asset_group_id` and `parent_campaign_id`.
   - Ad update rows must include `ad_id`, `parent_ad_group_id`, and `parent_campaign_id`.
5. Keep an export of the approved `old_name -> new_name` mapping with IDs before changing anything live.

## Conversion Tracking Use

Use the inventory CSV as the active Google Ads object crosswalk for the current transition:

- Keep `customer_id`, `campaign_id`, `ad_group_id`, `asset_group_id`, and `ad_id` in Google Ads QA exports and future build manifests.
- Use proposed `campaign_key`, `ad_group_key`, `asset_group_key`, and `ad_build_key` for future UTMs only after the row is reviewed and approved.
- Do not backfill historical reporting by name alone.
- Do not treat Google Ads ad rows as having a live display name; use `ad_id` plus build key for tracking and bulk-edit safety.

## Live Change Boundary

`Pending`

- No live campaign, ad group, asset group, ad, budget, bidding, status, conversion-action, or tracking-template changes were made.
- Before any live Google Ads rename or bulk change, export the affected rows from the CSV, review `current_name -> proposed_gads_name`, and get explicit approval.
