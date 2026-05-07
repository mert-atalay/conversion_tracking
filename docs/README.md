# CEFA Marketing Measurement Docs

Last updated: 2026-05-03

This directory is the governed documentation layer for the CEFA marketing measurement repo. It supports parallel work by conversion tracking, BigQuery, SEO, naming convention, and paid-media agents without forcing every topic into one document.

## Start Here

- [Governance](./00-governance/README.md): repo rules, source-of-truth order, agent responsibilities, contribution workflow.
- [Repository map](./00-governance/repo-map.md): where each type of update belongs.
- [Source-of-truth rules](./00-governance/source-of-truth-rules.md): how to resolve conflicts between live systems, repo docs, local CEFA sources, and external best practices.
- [Data taxonomy and source map](./00-governance/data-taxonomy.md): cross-workstream map for data sources, stable IDs, naming keys, conversion events, and reporting surfaces.
- [Workstream update template](./_templates/workstream-update-template.md): template for substantial updates.

## Workstreams

| Folder | Workstream | Use for |
|---|---|---|
| [10-conversion-tracking](./10-conversion-tracking/README.md) | Conversion tracking | Parent/franchise tracking, GTM, GA4, Google Ads, Meta, CAPI, sGTM, Measurement Protocol |
| [20-bigquery](./20-bigquery/README.md) | BigQuery and reporting data | Warehouse tables, marts, Looker/reporting contracts, offline conversion exports |
| [30-seo](./30-seo/README.md) | SEO measurement | Technical SEO, local SEO, Search Console, page taxonomy, sitemap measurement |
| [40-naming-convention](./40-naming-convention/README.md) | Naming convention | Meta naming, creative filenames, UTM rules, n8n naming guardrails |
| [50-paid-media](./50-paid-media/README.md) | Paid media execution | Platform launch QA, conversion action usage, optimization notes, account-level status |
| [60-master-data](./60-master-data/README.md) | Master data | School, program, location, CRM, GBP, and marketing-platform crosswalks |

## Historical Docs

Pre-governance docs still live directly under `docs/` and in existing phase folders. Keep those paths stable unless there is a clear reason to move them, because prior handoffs and other agents may already reference them.

New docs should go into the numbered workstream folders and be linked from the relevant workstream README.

## Working Rule

Use `Verified`, `Partial`, `Pending`, and `Open question` labels. Do not promote assumptions into source-of-truth docs.
