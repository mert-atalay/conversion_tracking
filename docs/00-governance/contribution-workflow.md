# Contribution Workflow

Last updated: 2026-05-03

## Before Adding A File

1. Read [repo-map.md](./repo-map.md).
2. Choose the narrowest workstream folder.
3. Check whether a workstream README already links the relevant current file.
4. If the update affects live tracking, platform configuration, or source-of-truth data, verify the current state first.

## File Naming

Use this pattern for dated operational docs:

```text
topic-name-YYYY-MM-DD.md
```

Use stable names for indexes and evergreen docs:

```text
README.md
event-taxonomy.md
source-of-truth-rules.md
```

## Required Sections For Handoffs

Use [workstream-update-template.md](../_templates/workstream-update-template.md) for larger updates.

Minimum sections:

- Purpose
- Current verified status
- Source evidence
- Decisions
- Open questions
- Next actions

## Commit Rules

- Documentation-only changes should not include plugin runtime edits unless the task explicitly covers both.
- Runtime plugin edits should include verification notes in the same PR/commit or an adjacent doc update.
- Do not commit local secrets, auth files, raw logs, or full platform exports.
