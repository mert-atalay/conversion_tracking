# CEFA Marketing Measurement Docs

Last updated: 2026-07-23

This directory is the governed documentation layer for the CEFA marketing measurement repo. It supports parallel work by conversion tracking, BigQuery, SEO, naming convention, and paid-media agents without forcing every topic into one document.

## Start Here

- [Measurement and activation program register](./00-governance/measurement-and-activation-program-register-2026-07-23.md): current live state, approved Stape and Google Cloud scope, external dependencies, build sequence, and production gates.
- [Governance](./00-governance/README.md): repo rules, source-of-truth order, agent responsibilities, contribution workflow.
- [Repository map](./00-governance/repo-map.md): where each type of update belongs.
- [Source-of-truth rules](./00-governance/source-of-truth-rules.md): how to resolve conflicts between live systems, repo docs, local CEFA sources, and external best practices.
- [Data taxonomy and source map](./00-governance/data-taxonomy.md): cross-workstream map for data sources, stable IDs, naming keys, conversion events, and reporting surfaces.
- [Repository structure audit](./00-governance/repository-structure-audit-2026-06-03.md): conservative cleanup decision, collision risks, and branch consolidation recommendation.
- [Workstream update template](./_templates/workstream-update-template.md): template for substantial updates.

## Workstreams

| Folder | Owner | Use for |
|---|---|---|
| [00-governance](./00-governance/README.md) | All agents | Repo rules, source-of-truth order, branch/doc structure, agent responsibilities |
| [10-conversion-tracking](./10-conversion-tracking/README.md) | Conversion tracking | Parent/franchise tracking, GTM, GA4, Google Ads, Meta, CAPI, sGTM, Measurement Protocol |
| [20-bigquery](./20-bigquery/README.md) | BigQuery/data | Warehouse tables, marts, Looker/reporting contracts, offline conversion exports |
| [30-seo](./30-seo/README.md) | SEO | Technical SEO, local SEO, Search Console, page taxonomy, sitemap measurement |
| [40-naming-convention](./40-naming-convention/README.md) | Naming convention | Meta/Google naming, creative filenames, UTM rules, n8n naming guardrails |
| [50-paid-media](./50-paid-media/README.md) | Paid media | Platform launch QA, conversion action usage, optimization notes, account-level status |
| [60-master-data](./60-master-data/README.md) | Master data | School, program, location, CRM, GBP, and marketing-platform crosswalks |

## Historical Docs

Pre-governance docs still live directly under `docs/` and in existing phase folders. Keep those paths stable unless there is a clear reason to move them, because prior handoffs and other agents may already reference them.

New docs should go into the numbered workstream folders and be linked from the relevant workstream README.

### Historical / Reference Areas

| Path | Status | Current owner / update new work here |
|---|---|---|
| `docs/*.md` legacy root docs | Mixed: current summaries, reference-only audits, and historical handoffs | Use the owner note at the top of each file; route new updates to the relevant numbered workstream. |
| [phase1a](./phase1a/README.md) | Current parent Phase 1A evidence | [10-conversion-tracking](./10-conversion-tracking/README.md) |
| [franchise-canada-phase1](./franchise-canada-phase1/README.md) | Current franchise Canada phase evidence | [10-conversion-tracking](./10-conversion-tracking/README.md) |
| [franchise-usa-phase1](./franchise-usa-phase1/README.md) | Current franchise USA phase evidence | [10-conversion-tracking](./10-conversion-tracking/README.md) |
| [franchise-transition-final-pack-v1](./franchise-transition-final-pack-v1/00-executive-summary-and-final-decision.md) | Historical package / reference bundle | [10-conversion-tracking](./10-conversion-tracking/README.md) |

## Working Rule

Use `Verified`, `Partial`, `Pending`, and `Open question` labels. Do not promote assumptions into source-of-truth docs.

New documentation belongs in the narrowest correct numbered workstream folder. Do not keep `main` and `codex/franchise-canada-tracking-plan` as parallel source-of-truth branches after PR consolidation.
