# CEFA Marketing Measurement Repo Instructions

This repo has two responsibilities:

1. Runtime code for the `CEFA Conversion Tracking` WordPress plugin.
2. Governed documentation for CEFA marketing measurement workstreams.

Keep those responsibilities separate.

## Repo Boundaries

- Runtime plugin code lives in the root PHP file, `includes/`, `assets/`, `snippets/`, and release files.
- Workstream documentation lives under numbered folders in `docs/`.
- Reusable reference data should live under `data/reference/`.
- Do not put scratch notes, raw exports, secrets, OAuth tokens, platform credentials, or large temporary files in this repo.
- Do not change live GTM, GA4, Google Ads, Meta, WordPress, or BigQuery settings unless the user explicitly asks for live execution.

## Workstream Map

- `docs/10-conversion-tracking/`: parent, franchise Canada, franchise USA, GTM, GA4, Ads/Meta conversion contracts, CAPI, sGTM, Measurement Protocol.
- `docs/20-bigquery/`: datasets, marts, schemas, QA checks, offline conversion exports, reporting data contracts.
- `docs/30-seo/`: technical SEO, local SEO, Search Console, sitemap/page taxonomy, SEO measurement.
- `docs/40-naming-convention/`: CEFA Meta naming convention, creative filenames, UTM conventions, n8n naming guardrails.
- `docs/50-paid-media/`: ad account structure, launch QA, optimization notes, platform conversion action status, budget-safety references.
- `docs/60-master-data/`: schools, programs, locations, CRM/system crosswalks, canonical reference tables.
- `docs/00-governance/`: source-of-truth rules, agent responsibilities, repo map, and contribution workflow.

## Agent Rules

- Start at `docs/00-governance/repo-map.md` before adding new documentation.
- Update the relevant workstream `README.md` when adding or changing docs in that workstream.
- If a decision affects more than one workstream, update `docs/00-governance/source-of-truth-rules.md` or add a cross-link from the relevant workstream README.
- Keep parent `cefa.ca`, franchise Canada `franchise.cefa.ca`, and franchise USA `www.franchisecefa.com` separate unless the document is explicitly cross-property.
- For conversion tracking, `school_uuid` is the parent school join key unless a future verified source changes that.
- Do not promote assumptions into verified sections. Use `Verified`, `Partial`, `Pending`, or `Open question`.
- If a file is mainly a source index or handoff for another agent, say that directly in the file.

## Commit Hygiene

- Keep runtime plugin changes and documentation-only changes in separate commits when practical.
- Do not commit generated ZIPs unless the user explicitly asks for a release package to be tracked.
- Do not rewrite another agent's work without reading it first.
