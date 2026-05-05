# Meta Creative Build Import Manifest Contract

Last updated: 2026-05-04

## Scope

| Field | Value |
| --- | --- |
| Workstream | `docs/40-naming-convention/` |
| Platform | Meta Ads |
| Applies to | CEFA Early Learning parent campaigns and CEFA Franchisor campaigns |
| Extends | NC2 naming, active Meta object ID inventory, v20/final-v3 workbook review |
| Manifest template | [`data/reference/cefa-meta-creative-build-manifest-template-2026-05-04.csv`](../../data/reference/cefa-meta-creative-build-manifest-template-2026-05-04.csv) |
| Live Meta writes made | No |

## Purpose

This contract adds the missing operational layer between naming rules and Meta execution.

The naming convention alone is not enough for near-perfect bulk upload or n8n execution. The build/import layer must state exactly which creative and copy goes into which campaign/ad set/ad, which IDs are used, which name will be generated, which URL tags will be applied, and whether the row is safe to export.

## Status

`Verified`

- The current repo has an active Meta object inventory with campaign, ad set, and ad IDs for CEFA Early Learning and CEFA Franchisor objects that delivered from 2026-04-05 through 2026-05-04.
- The v20/final-v3 workbook direction is correct: copy, creative, Meta build, and import-ready areas are separated.
- CEFA guardrails require imported or API-created Meta objects to default to `PAUSED`.
- The parent program dropdown must separate user-facing labels from machine-safe reporting tokens.

`Partial`

- This manifest is a governed schema and workflow contract, not a completed workbook implementation.
- It has not yet been validated against a fresh Meta Ads Manager bulk import template export.
- Creative asset IDs, image hashes, video IDs, and Drive/SharePoint file URLs are not populated in this repo.
- Destination URLs still need final reconciliation against the governed school/form URL source and the canonical school dimension.

`Pending`

- CEFA approval of final parent program-token combinations.
- CEFA approval of the exact import path: manual Meta bulk import, n8n-generated file, paused API creation, or a staged combination.
- A fresh Ads Manager export/import template check before any first real upload.

`Open question`

- Whether budget amounts in the build manifest should stay as planning-only fields or become a separate approved budget-change workflow. Default answer: planning-only unless explicitly approved.

## Required Sheet Or Table Layers

Use these layers in the workbook, Google Sheet, n8n data tables, Airtable, Supabase, or another approved system. The names can vary, but the boundaries should not.

| Layer | Owner | Purpose | Live-write risk |
| --- | --- | --- | --- |
| `OBJECT_DESTINATIONS` | MB / automation | Approved campaign and ad set destinations, including current IDs and keys. | Low |
| `CREATIVE_ASSET_REGISTRY` | GD / automation | Creative files, file URLs, asset IDs, hashes, format, dimensions, and usage status. | Medium if it triggers uploads |
| `COPY_LIBRARY` | CW / MB | Approved primary text, headline, description, CTA, and copy keys. | Low |
| `BUILD_MANIFEST` | MB / automation | One row per intended ad create/update/rename using approved destinations, copy, and creative. | Medium |
| `IMPORT_READY` | Automation | Only rows that passed QA and are ready for Meta import/export. | High |
| `IMPORT_AUDIT` | Automation | Post-import IDs, old/new names, approval status, user, timestamp, and result. | Low |
| `QA_REPORT` | Automation | Blockers and warnings for rows that cannot be exported. | Low |

## Build Manifest Columns

Use the template CSV as the minimum header contract. The workbook can add helper columns, but import automation should preserve these fields.

| Column group | Required fields | Rule |
| --- | --- | --- |
| Batch identity | `manifest_version`, `build_batch_id`, `row_id`, `action` | Every row must be traceable to a build batch and one action. |
| Account | `account_alias`, `account_id` | Use `parent` or `franchise`; account ID should match the Meta object inventory. |
| Destination | `campaign_id`, `campaign_key`, `adset_id`, `ad_set_key`, `ad_id` | Existing objects must be matched by ID first, not by name. |
| Budget grouping | `budget_group`, `location_slug`, `location_name` | Required for LSM/location work; CORP/franchise rows can use a group/topic where no school location exists. |
| Program/topic | `program_token`, `program_label`, `franchise_topic` | Parent rows use program tokens; franchise rows use franchise topic/offer. |
| Creative | `creative_asset_key`, `creative_file_url`, `creative_asset_id`, `creative_format`, `creative_dimensions`, `creative_duration_seconds`, `visual_concept` | File identity and Meta asset identity stay separate. |
| Copy | `copy_key`, `copy_angle`, `primary_text`, `headline`, `description`, `cta` | Rendered final copy only. No unresolved placeholders. |
| URL/UTM | `destination_url_type`, `destination_url`, `url_tags`, `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term` | URL tags are generated from stable keys, not from current Meta names. |
| Generated names | `generated_campaign_name`, `generated_adset_name`, `generated_ad_name` | Must match NC2 naming rules before export. |
| Import status | `meta_campaign_status`, `meta_adset_status`, `meta_ad_status` | Default to `PAUSED`. |
| Budget planning | `requested_budget`, `approved_budget` | Planning metadata only unless a separate live budget approval is documented. |
| QA and approval | `qa_status`, `qa_errors`, `qa_warnings`, `approval_status`, `approved_by`, `approved_at` | `IMPORT_READY` rows require QA pass and approval. |
| Publishing audit | `publish_status`, `meta_import_batch_id`, `meta_result_id`, `notes` | Required for post-import reconciliation. |

## Action Rules

| Action | Required IDs before export | ID rule |
| --- | --- | --- |
| `rename_campaign` | `campaign_id` | Compare current name to generated campaign name before rename. |
| `rename_adset` | `campaign_id`, `adset_id` | Compare current ad set name to generated ad set name before rename. |
| `rename_ad` | `campaign_id`, `adset_id`, `ad_id` | Compare current ad name to generated ad name before rename. |
| `create_ad` | `campaign_id`, `adset_id` | `ad_id` stays blank until post-import sync. |
| `update_ad` | `campaign_id`, `adset_id`, `ad_id` | Use only when changing an existing ad object by ID. |
| `create_adset` | `campaign_id` | `adset_id` stays blank until post-import sync; status must be `PAUSED`. |
| `create_campaign` | none at creation time | Requires separate approval because budget/objective/settings risk is higher. |
| `pause_only` | target object ID | Allowed only for explicitly selected objects; never use name-only matching. |

## Parent Program Token Contract

Parent ad-level creative and copy rows must include a program dropdown.

| User-facing label | Machine token | Use |
| --- | --- | --- |
| All Programs | `all` | Parent campaign or ad applies to CEFA Baby, JK1, JK2, and JK3 together. |
| CEFA Baby | `cefa_baby` | CEFA Baby-specific creative/copy. |
| JK1 | `jk1` | JK1-specific creative/copy. |
| JK2 | `jk2` | JK2-specific creative/copy. |
| JK3 | `jk3` | JK3-specific creative/copy. |
| Approved combo | `jk1+jk2`, `jk2+jk3`, etc. | Only use combinations approved by CEFA before import. |

Rules:

- Parent `all` means all parent programs, not franchise.
- Keep `program_label` for humans and `program_token` for reporting, filenames, keys, and validation.
- Franchise rows should leave parent `program_token` blank or `not_applicable` and use `franchise_topic` / offer fields instead.
- Do not change franchise topic/offer taxonomy as part of the parent program dropdown unless CEFA approves a franchise naming revision.

## URL And UTM Contract

Every importable row must generate final URL tags.

```text
utm_source=meta
utm_medium=paid_social
utm_campaign={campaign_key}
utm_content={ad_data_key}
utm_term={ad_set_key}
```

Rules:

- `utm_campaign` comes from the approved campaign key.
- `utm_content` comes from the approved ad data key or generated ad key.
- `utm_term` comes from the approved ad set key.
- Destination URL and URL tags must be separate fields.
- Parent school rows should distinguish `School URL` from `Inquiry Form URL`.
- Do not generate UTMs from visible campaign/ad names after launch, because names can change.

## QA Gates Before Import Ready

A row cannot enter `IMPORT_READY` unless all required gates pass.

| Gate | Block condition |
| --- | --- |
| Destination | Existing campaign/ad set/ad target is missing the required ID. |
| Naming | Generated names do not match the current NC2 contract. |
| Current object match | Update/rename row ID exists but current name/account does not match the reviewed inventory row. |
| Status | Any generated campaign, ad set, or ad status is not `PAUSED`. |
| Program/topic | Parent row has no approved `program_token`; franchise row uses a parent program token incorrectly. |
| Copy | Primary text, headline, description, or CTA is missing where required. |
| Placeholder | Rendered copy contains unresolved or unsupported placeholders. |
| Copy length | Length flags are not visible in import QA. Hard failures and warnings must be separated. |
| Creative file | Creative asset URL/key is missing, duplicated unexpectedly, or format does not match `creative_format`. |
| Creative ID | Update/API rows that require a Meta image hash or video ID do not have one. |
| URL/UTM | Destination URL or final URL tags are blank or malformed. |
| Duplicate keys | Duplicate generated campaign/ad set/ad names or keys exist in the same build batch. |
| Review status | Source inventory row is marked `needs_review`. |
| Approval | `approval_status` is not approved for the intended action. |

## n8n Phase 1 Boundary

For the first n8n/MCP phase, allowed actions are:

- validate source tabs and controlled values;
- render final copy;
- generate names, keys, and URL tags;
- generate the Meta import file;
- sync IDs after manual import or approved paused API creation;
- write audit rows and QA reports.

Blocked without explicit CEFA approval:

- activating campaigns, ad sets, or ads;
- changing live budgets;
- deleting objects;
- changing optimization goals, attribution settings, conversion events, or pixel/dataset settings;
- creating active objects;
- running direct API launch workflows.

## Workbook Changes Required

The v20/final-v3 workbook should be updated to include or enforce this contract:

1. Add a `BUILD_MANIFEST` layer or make `META_AD_BUILD_MB` match the manifest template.
2. Keep `IMPORT_READY` generated-only; do not allow hand edits except approval fields.
3. Add URL tag output fields and separate `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, and `utm_term`.
4. Add `program_label` and `program_token` dropdowns for parent copy/creative/ad rows.
5. Add franchise topic/offer fields that are separate from parent program tokens.
6. Add row-level `action`, `qa_status`, `approval_status`, and `publish_status`.
7. Add duplicate-name/key detection across the current build batch.
8. Add an import audit output that stores IDs returned by Meta after import or API creation.

## Relationship To Current GitHub Files

- Use [Meta naming NC2 active last-30 inventory](./meta-naming-nc2-active-last-30-inventory-2026-05-04.md) as the ID crosswalk for existing campaign, ad set, and ad rows.
- Use [Budget-driven Meta naming v20 final-v3 review](./budget-driven-meta-naming-v20-final-v3-review-2026-05-04.md) as the workbook readiness review.
- Use the manifest template CSV as the header contract for future workbook/n8n import rows.

## Live Change Boundary

`Pending`

This document does not approve live Meta changes. It defines the controlled structure required before CEFA should generate import files, run n8n import workflows, or ask Codex to create/update ads.
