# Repository Map

Last updated: 2026-05-03

## Purpose

This repo is the shared GitHub home for CEFA marketing measurement implementation and documentation. It should let multiple agents work in parallel without overwriting each other or mixing unrelated workstreams.

## Top-Level Areas

| Path | Purpose | Primary owner |
|---|---|---|
| `cefa-conversion-tracking.php` | WordPress plugin bootstrap | Conversion tracking/plugin agent |
| `includes/` | WordPress plugin PHP classes | Conversion tracking/plugin agent |
| `assets/js/` | Browser tracking bridge | Conversion tracking/plugin agent |
| `snippets/` | Temporary runtime snippets, especially franchise WPCode fallback | Conversion tracking/plugin agent |
| `docs/00-governance/` | Repo rules, routing, source-of-truth decisions | All agents |
| `docs/10-conversion-tracking/` | Tracking implementation and platform measurement plans | Conversion tracking agent |
| `docs/20-bigquery/` | Warehouse, marts, schemas, QA, offline conversion contracts | BigQuery/data agent |
| `docs/30-seo/` | SEO measurement, local SEO, Search Console, page taxonomy | SEO agent |
| `docs/40-naming-convention/` | Meta naming convention, creative taxonomy, UTM naming | Naming convention agent |
| `docs/50-paid-media/` | Paid-media execution, Ads/Meta action status, launch QA | Paid-media agent |
| `docs/60-master-data/` | Schools, programs, CRM/system crosswalks, canonical tables | Shared master-data owner |
| `docs/_templates/` | Reusable templates for future docs | All agents |
| `data/reference/` | Machine-readable reference data | Shared, with owner noted per file |
| `dist/` | Local release ZIPs/build output | Release task only |

## Existing Historical Docs

Many pre-governance files still live directly under `docs/` or in existing phase folders. Do not move them unless there is a clear reason, because other docs and agents already reference those paths.

New documents should go into the numbered workstream folders. Existing documents can be linked from the appropriate workstream README.

## Recommended New-File Routing

| If the new file is about... | Put it here |
|---|---|
| Parent inquiry tracking, GTM, GA4, Ads/Meta conversion mapping | `docs/10-conversion-tracking/parents/` or existing parent docs if already established |
| Franchise Canada/USA tracking | `docs/10-conversion-tracking/franchise-canada/` or `docs/10-conversion-tracking/franchise-usa/` |
| BigQuery table design, SQL, Looker/warehouse QA | `docs/20-bigquery/` |
| SEO page mapping, Search Console, local SEO tracking | `docs/30-seo/` |
| Meta naming, creative file naming, NC1, UTM naming | `docs/40-naming-convention/` |
| Ads account structure, optimization, platform launch QA | `docs/50-paid-media/` |
| School/program/location CRM crosswalks | `docs/60-master-data/` |

## Do Not Mix

- Do not put paid-media budget recommendations inside conversion-tracking implementation docs.
- Do not put SEO content recommendations inside GTM/GA4 docs.
- Do not put naming convention changes inside ad optimization notes without linking the naming source.
- Do not put school/program master data inside plugin code comments.
- Do not put temporary test logs into source-of-truth docs.
