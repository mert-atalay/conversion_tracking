# Budget-Driven Meta Naming v19 Review

Last updated: 2026-05-04

## Scope

| Field | Value |
| --- | --- |
| Workstream | `docs/40-naming-convention/` |
| Platform | Meta Ads naming and bulk import prep |
| Package | CEFA Budget-Driven Meta Naming + Bulk Builder v19 |
| Live writes made | No |

## Source Package

| Item | Status | Link |
| --- | --- | --- |
| Drive folder | `Verified` | [CEFA v19 naming package](https://drive.google.com/drive/folders/1uVG9KM-C94covrmZqle20ja4NJKC3taZ) |
| Workbook | `Verified` | [CEFA_Budget_Driven_Meta_Naming_Bulk_Builder_v19_FINAL (1).xlsx](https://docs.google.com/spreadsheets/d/1n4SehWNb6UfhNDkYtKyYOS19a-v_Eijq/edit?usp=drivesdk&ouid=100264075182330360487&rtpof=true&sd=true) |
| n8n workflow guide | `Verified` | [CEFA_Budget_Driven_Workflow_n8n_Automation_v19 (1).md](https://drive.google.com/file/d/19w9C3JbCmPHF3IttT1n4h_K__5qDfffw/view?usp=drivesdk) |
| n8n blueprint JSON | `Verified` | [CEFA_n8n_Budget_Driven_Meta_Bulk_Blueprint_v19 (1).json](https://drive.google.com/file/d/1SQJMmURfY1oi2xGSmXoW-FJR0O5yRW9B/view?usp=drivesdk) |

## Review Status

`Verified`

- The Drive folder contains the v19 workbook, n8n workflow guide, and n8n blueprint JSON.
- The workbook presents v19 as a budget-driven flow from executive budget planning to media-plan rows, campaign names/keys, copy, creative, Meta build rows, stakeholder review, and import-ready rows.
- The workbook month horizon is July 2025 through December 2027, with monthly columns `H:AK` and total column `AL` in the budget tabs.
- The workbook states it avoids modern-only formulas such as `XLOOKUP`, `LET`, `FILTER`, `UNIQUE`, and `TEXTJOIN`.
- The n8n blueprint positions phase 1 as human-in-the-loop and disallows initial direct launch, campaign activation, or budget changes without approval.

`Partial`

- The workbook structure and formulas were reviewed for naming/workflow fit, but formula outputs were not fully audited against the live CEFA budget workbook and a current Meta bulk import/export.
- The v19 naming rules materially differ from the current `NC1` contract, so this should be treated as a candidate new version until approved.

`Pending`

- Validate sample rows against the canonical CEFA budget workbook.
- Validate `META_IMPORT_READY` output against the current Meta bulk import template.
- Decide whether v19 supersedes `NC1` as `NC2` or remains a separate budget-planning builder.

`Open question`

- `META_IMPORT_READY` appears to set Meta campaign, ad set, and ad statuses to `ACTIVE` when a row is marked `Approved`. CEFA guardrails require imported or API-created Meta objects to default to paused unless explicitly approved for launch. Clarify whether `Approved` means final launch approval or only internal naming/content approval.
- v19 campaign names remove `{FundingTag}` from the current `NC1` campaign pattern. Confirm whether this is intentional before replacing `NC1`.
- v19 uses `{PlatformTag}` rather than fixed `META`. Confirm whether the workbook is intended to support non-Meta naming later.
- Confirm the canonical source for school, region, and location slugs before bulk use.

## v19 Naming Rules

Campaign:

```text
CEFA | {Scope} | {Activation} | {LocationOrGroup} | {PlatformTag} | {Objective} | {Funnel} | {Theme} | {YYYYMM} | {Seq}
```

Ad set:

```text
{Persona} | {AudienceType} | {Geo} | {Placement}
```

Meta ad:

```text
{FormatTag} | {VisualConcept} | {CopyAngle} | v{#}
```

Copy key:

```text
{campaign_key}__{persona_slug}__{angle_slug}__cp##
```

Creative group key:

```text
{campaign_key}__{format}__{concept_slug}__cr##__v#
```

Creative file:

```text
{creative_group_key}__card##?__{aspect}__{width}x{height}.{ext}
```

UTM campaign:

```text
Use campaign_key where possible.
```

UTM content:

```text
Derived from the ad data key.
```

## Feedback

The v19 workbook is a stronger operating design than a manual naming sheet because it makes budget/media-plan rows the upstream source for campaign names and keys. That is useful for CEFA if MB, copy, creative, and stakeholders will all work from the same workbook.

The main blocker is governance, not spreadsheet design. v19 changes the campaign contract from current `NC1`, especially by removing `{FundingTag}` and making names budget/media-plan driven. Treat it as candidate `NC2`, not a silent update to `NC1`.

The highest-risk implementation detail is the `ACTIVE` status behavior in `META_IMPORT_READY`. For phase 1, imported rows should stay `PAUSED` by default unless there is a separate, explicit final launch approval field.

Keeping the workbook itself in Drive and storing the Drive URL plus distilled rules in GitHub is the right approach. GitHub should hold the durable contract, review status, and guardrails; Drive should hold the working spreadsheet.

## Recommended Next Step

Before sharing v19 as the team source of truth, update or clarify the import status rule so internal approval does not accidentally become live Meta activation. After that, validate a small batch against the actual CEFA budget workbook and a current Meta import file, then approve it as `NC2` if the campaign-pattern change is intentional.
