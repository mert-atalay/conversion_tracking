# SEO Restart Handoff

Last updated: 2026-05-03

## Purpose

This file gives the SEO agent a clean restart point in the shared GitHub measurement repo. It exists because the older CEFA SEO thread became too large to continue reliably and had not yet written its current SEO context into this repo's governed `docs/30-seo/` workstream.

## Scope

| Field | Value |
|---|---|
| Workstream | SEO measurement |
| Primary repo folder | `docs/30-seo/` |
| Prior SEO thread | `019d3c3f-fb59-7d23-aaf8-e6360c218eeb` |
| Verification date | 2026-05-03 |
| Live writes made | No |

## Current Verified Status

| Area | Status | Current state |
|---|---|---|
| Old SEO thread runtime | Verified | Thread `019d3c3f-fb59-7d23-aaf8-e6360c218eeb` is not a healthy active work surface. Local Codex state showed no active turn on resume, and a background memory job failed because the thread exceeded the model context window. |
| Old SEO thread size | Verified | The local session file is about 26.5 MB with 7,673 JSONL lines, so future SEO work should start in a fresh thread with this handoff instead of resuming the old thread. |
| SEO GitHub workstream | Verified | Before this handoff, `docs/30-seo/` only had `README.md`; no committed SEO status file existed in the governed workstream folder. |
| CEFA GSC seasonality source file | Verified | Existing local artifact: `/Users/matthewbison/Desktop/cefa-nexus/CEFA/.agency/artifacts/seo/cefa-gsc-parent-query-seasonality-report-2025-04-to-2026-03.md`. |
| GSC report data window | Partial | The report covers 2025-04-01 through 2026-03-31. It is verified as an existing artifact, but not current after 2026-03-31. |
| DataForSEO sector source files | Verified | Existing local artifacts include `cefa-sector-keyword-research-dataforseo-canada-2026-04-21.csv`, `.json`, and `cefa-sector-keyword-cluster-seasonality-dataforseo-canada-2026-04-21.csv`. |
| AI/LLM SEO source files | Verified | Existing local artifacts include `cefa-total-ai-seo-parent-search-report-2026-04-22.md`, `cefa-llm-mentions-parent-question-visibility-2026-04-22.md`, and related CSV/JSON files. |
| Current Search Console freshness | Pending | A restarted SEO agent must rerun or verify live GSC access before claiming data after 2026-03-31. |
| Current DataForSEO freshness | Pending | A restarted SEO agent must rerun or verify DataForSEO if new keyword volume, SERP, or competitor data is needed. |

## Existing SEO Evidence To Reuse

| Evidence | Status | Notes |
|---|---|---|
| GSC parent-query seasonality report | Partial | Source file says it used Search Console property `https://cefa.ca/` via CEFA GSC MCP/ADC auth as `mert.atalay@cefa.ca`. It pulled 494,685 raw daily query rows, 21,115 classified parent/branded queries, and 3,905 literal question queries for 2025-04-01 through 2026-03-31. |
| GSC branded/non-branded query analysis | Partial | Useful for parent-intent SEO planning, but should not be treated as current after 2026-03-31 without a new pull. |
| DataForSEO Canada sector research | Partial | Existing cleaned sector dataset and cluster files are useful for market-wide keyword context, but should be refreshed for current campaign or content decisions. |
| GBP category guidance from old thread | Partial | Prior discussion recommended tight GBP categories around `Day care center` and `Preschool`, while avoiding `Montessori school` unless locations are publicly positioned and operated as Montessori schools. This needs a dedicated `local-seo-utm-and-gbp-measurement.md` file before it becomes a workstream reference. |
| Franchise Canada sitemap issue from old thread | Partial | Prior checks found `franchise.cefa.ca/school-sitemap.xml` contained many `/school/.../` URLs returning 404. This needs a dedicated sitemap/page-taxonomy status file before it becomes a workstream reference. |

## Restart Instructions For SEO Agent

| Step | Status | Instruction |
|---|---|---|
| 1 | Verified | Start from `docs/README.md`, `docs/00-governance/repo-map.md`, `docs/00-governance/source-of-truth-rules.md`, `docs/00-governance/agent-responsibilities.md`, and `docs/30-seo/README.md`. |
| 2 | Verified | Use this file as the SEO restart handoff. Do not rely on the old oversized thread as the active working surface. |
| 3 | Verified | Keep SEO findings in `docs/30-seo/` and update `docs/30-seo/README.md` when adding important files. |
| 4 | Verified | Mark every fact as `Verified`, `Partial`, `Pending`, or `Open question`; do not convert old-thread advice into verified repo guidance without rechecking or citing source files. |
| 5 | Verified | Do not redefine conversion events, school identity keys, paid-media budgets, or naming conventions in SEO docs. Link to the correct workstream instead. |

## Recommended First SEO Files

| File | Status | Purpose |
|---|---|---|
| `search-console-measurement-status.md` | Pending | Current GSC access, properties, data windows, core query groups, and freshness limits. |
| `local-seo-utm-and-gbp-measurement.md` | Pending | GBP category, UTM, local listing, and daycare/childcare/preschool measurement guidance. |
| `page-taxonomy-reporting-map.md` | Pending | SEO page types, sitemap status, canonical URLs, and reporting aliases for GA4/BigQuery. |
| `franchise-canada-sitemap-status.md` | Pending | Franchise Canada sitemap and 404 URL issue, if still live after rechecking. |

## Current Open Questions

| Question | Status | Owner workstream |
|---|---|---|
| Are GSC properties still available through `mert.atalay@cefa.ca` in the current runtime? | Pending | SEO |
| Has Search Console data after 2026-03-31 been pulled and classified? | Pending | SEO |
| Are the `franchise.cefa.ca` school sitemap 404 URLs still live? | Open question | SEO |
| Should CEFA GBP primary category remain `Day care center`, switch to `Preschool`, or vary by location after local SERP review? | Open question | SEO |
| Which SEO page taxonomy should be used as the reporting alias layer in BigQuery and Looker? | Pending | SEO and BigQuery |

## Source Evidence

- Verified from local Codex state/logs and the local SEO artifact folder on 2026-05-03.
- No live Search Console, DataForSEO, WordPress, sitemap, or GBP writes were made by this handoff update.
