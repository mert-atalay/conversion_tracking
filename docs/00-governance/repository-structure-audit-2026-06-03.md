# Repository Structure Audit - 2026-06-03

Status: `Verified` for repository tree, branch comparison, and governance-file review on 2026-06-03. Status is `Partial` for document-level factual freshness because this audit checks structure, ownership, and collision risk, not every marketing/tracking claim inside every document.

## Scope

This audit checks whether the CEFA `conversion_tracking` GitHub repo is structurally safe for multiple workstreams and agents.

Checked surfaces:

- Local branch: `codex/franchise-canada-tracking-plan`
- Remote repo: `mert-atalay/conversion_tracking`
- Remote branch spot-check through GitHub connector
- Governance docs in `docs/00-governance/`
- Workstream READMEs in `docs/10-conversion-tracking/`, `docs/20-bigquery/`, `docs/30-seo/`, `docs/40-naming-convention/`, `docs/50-paid-media/`, and `docs/60-master-data/`
- Current tracked docs and reference data tree

## Executive Decision

The repo structure is directionally correct, but the branch strategy is now misleading.

Decision: combine the broad `codex/franchise-canada-tracking-plan` branch into `main` through a reviewed PR, then stop treating the branch as a separate "franchise tracking plan."

Reason: the branch now contains parent tracking, franchise Canada, franchise USA, naming convention, paid media, BigQuery/data, master data, reference CSVs, and plugin runtime changes. It is no longer a narrow franchise plan.

Do not combine all documents into one file. Combine the branch into `main`, while keeping the numbered workstream folders distinct.

## Current Structure Health

Status: `Verified`

The numbered folder model is sound:

| Folder | Keep as owner for |
|---|---|
| `docs/00-governance/` | Repo rules, source-of-truth order, agent ownership, structure audits |
| `docs/10-conversion-tracking/` | Parent/franchise tracking, GTM, GA4, Ads/Meta conversion contracts, CAPI, sGTM, Measurement Protocol |
| `docs/20-bigquery/` | Warehouse, marts, reporting data contracts, QA, offline conversion exports |
| `docs/30-seo/` | SEO measurement, Search Console, local SEO, page/page-taxonomy measurement |
| `docs/40-naming-convention/` | Campaign/ad/ad-set naming, creative filenames, copy keys, UTM rules, n8n naming guardrails |
| `docs/50-paid-media/` | Paid-media execution, launch QA, conversion action usage, optimization/status notes |
| `docs/60-master-data/` | Schools, programs, locations, CRM/system crosswalks, canonical reference tables |
| `data/reference/` | Machine-readable CSV/JSON/YAML reference inputs that support the docs |

This separation should stay.

## Collision Risks

Status: `Partial`

The main risk is old and new documentation coexisting without a clear "current owner" label.

| Area | Collision risk | Recommended owner |
|---|---|---|
| Root-level docs under `docs/*.md` | Many pre-governance docs overlap with `docs/10-conversion-tracking/` and `docs/60-master-data/`. | Keep stable for now; route new updates through numbered workstream READMEs. |
| `docs/phase1a/` | Parent Phase 1A docs overlap with `docs/10-conversion-tracking/`. | Treat as historical/current phase evidence; new parent tracking summaries go in `docs/10-conversion-tracking/`. |
| `docs/franchise-canada-phase1/` | Franchise Canada phase docs overlap with `docs/10-conversion-tracking/`. | Keep phase folder for detailed evidence; summarize current state in `docs/10-conversion-tracking/`. |
| `docs/franchise-usa-phase1/` | Franchise USA phase docs overlap with `docs/10-conversion-tracking/`. | Keep phase folder for detailed evidence; summarize current state in `docs/10-conversion-tracking/`. |
| `docs/franchise-transition-final-pack-v1/` | Cross-property transition pack includes parent, franchise Canada, franchise USA, Meta, GTM, CAPI, and roadmap material. | Treat as a packaged historical decision bundle; do not add new daily updates there. |
| Root school/program docs vs `docs/60-master-data/` | `canonical-school-program-taxonomy` and `known-school-program-reference-table` overlap with master-data ownership. | `docs/60-master-data/` owns future master-data updates; root docs remain linked evidence until migrated. |
| AI-ready naming/conversion reference | `docs/40-naming-convention/cefa-ai-naming-conversion-reference-2026-05-20.md` intentionally summarizes multiple workstreams. | Keep it as an AI briefing/index, not as the canonical replacement for source docs. |
| Paid-media conversion action notes | Could drift between `docs/10-conversion-tracking/`, `docs/40-naming-convention/`, and `docs/50-paid-media/`. | Conversion definitions live in `10`; naming/UTMs live in `40`; platform execution and launch QA live in `50`. |

## Branch Recommendation

Status: `Verified`

Current branch comparison shows `codex/franchise-canada-tracking-plan` is ahead of `main` with broad repo changes, including:

- plugin/runtime changes;
- data reference README and active object inventory CSVs;
- governance data taxonomy;
- conversion-tracking docs;
- BigQuery/data docs;
- naming convention docs;
- master-data docs;
- franchise Canada/USA phase updates.

Recommended GitHub workflow:

1. Open or update a PR from `codex/franchise-canada-tracking-plan` into `main`.
2. Review runtime plugin changes separately from documentation-only changes where possible.
3. Merge the branch into `main` once reviewed.
4. After merge, delete or stop using `codex/franchise-canada-tracking-plan` for new work.
5. Use future branch names that match scope, for example:
   - `codex/measurement-governance-cleanup`
   - `codex/naming-convention-v21`
   - `codex/parent-tracking-phase1a`
   - `codex/franchise-usa-tracking`

Do not maintain `main` and `codex/franchise-canada-tracking-plan` as parallel source-of-truth branches.

## Target Documentation Model

Status: `Recommended`

Use this as the target structure:

```text
README.md
cefa-conversion-tracking.php
includes/
assets/
snippets/
data/
  reference/
docs/
  README.md
  00-governance/
  10-conversion-tracking/
    parent/
    franchise-canada/
    franchise-usa/
    cross-property/
    server-side/
  20-bigquery/
  30-seo/
  40-naming-convention/
  50-paid-media/
  60-master-data/
  90-archive/
    legacy-phase-docs/
```

The subfolders under `docs/10-conversion-tracking/` and `docs/90-archive/` are a future cleanup target, not an immediate move requirement.

## Migration Plan

Status: `Recommended`

Phase 1: governance cleanup only.

- Keep historical paths stable.
- Add this audit to `docs/00-governance/`.
- Link this audit from the governance README.
- Merge the broad branch into `main` through PR review.

Phase 2: owner-label cleanup.

- Add a "Current owner / update here" note to root-level historical docs.
- Add links from root-level docs to their owning workstream README.
- Mark historical package docs as `Reference only` or `Historical package` where appropriate.

Phase 3: optional file moves.

- Move only after a link map is created.
- Prefer moving old phase docs under `docs/90-archive/legacy-phase-docs/` only if old paths are no longer needed by agents or humans.
- If a file is moved, leave a short stub at the old path pointing to the new path unless CEFA approves breaking old links.

## Rules Going Forward

Status: `Verified`

- New docs must go to the narrowest numbered workstream folder.
- Existing historical docs can remain where they are, but should be linked from the owning workstream README.
- Cross-workstream summaries are allowed only when they clearly identify their owning source docs.
- Do not put naming rules in paid-media execution docs except as links to `docs/40-naming-convention/`.
- Do not put conversion-event definitions in SEO, naming, or paid-media docs except as links to `docs/10-conversion-tracking/`.
- Do not put school/program canonical IDs in plugin comments or naming docs; link to `docs/60-master-data/`.
- Do not treat the branch name as an ownership label. The branch is broad and should be merged into `main`.

## Subagent / Specialist Routing

Status: `Recommended`

No subagent is required for the structural audit itself. For future migration work:

- Conversion tracking owner should review moves affecting `docs/10-conversion-tracking/`, `docs/phase1a/`, and franchise phase folders.
- BigQuery/data owner should review `docs/20-bigquery/` and `data/reference/`.
- Naming convention owner should review `docs/40-naming-convention/` and naming-related reference CSVs.
- Paid-media owner should review `docs/50-paid-media/`.
- Master-data owner should review root school/program docs and `docs/60-master-data/`.

## Bottom Line

Status: `Verified`

The repo does not need one giant combined tracking plan. It needs one canonical default branch, `main`, with distinct workstream folders.

The broad `codex/franchise-canada-tracking-plan` branch should be merged into `main` after review because it now contains the real shared CEFA measurement structure, not only franchise work.
