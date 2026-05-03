# Agent Responsibilities

Last updated: 2026-05-03

## Purpose

This file keeps the CEFA agents from writing over each other or mixing scopes.

## Workstream Ownership

| Agent / role | Primary folder | Owns | Does not own |
|---|---|---|---|
| Conversion tracking parent/franchise agent | `docs/10-conversion-tracking/` plus plugin runtime files | DataLayer contracts, GTM/GA4/Ads/Meta conversion mapping, event IDs, attribution bridge, CAPI/sGTM roadmap | Paid-media optimization decisions, SEO copy, naming taxonomy changes |
| BigQuery/data agent | `docs/20-bigquery/` and `data/reference/` when appropriate | Dataset/mart contracts, SQL plans, QA checks, offline conversion exports, source-to-mart mapping | Live ad platform changes unless explicitly approved |
| SEO agent | `docs/30-seo/` | Technical SEO, local SEO, Search Console measurement, page taxonomy, sitemap status | Paid-media campaign decisions or conversion source-of-truth changes |
| Naming convention agent | `docs/40-naming-convention/` | NC1 naming, creative filenames, copy keys, campaign/ad/ad set naming, n8n naming guardrails | Live budget changes, conversion action definitions |
| Paid-media agent | `docs/50-paid-media/` | Ads account structure, launch QA, optimization notes, platform action status, conversion usage in bidding | Runtime plugin code, canonical school/program IDs |
| Master-data owner / shared agent | `docs/60-master-data/` and `data/reference/` | School/program/location/CRM crosswalks, canonical reference tables | Platform mapping decisions unless linked back to tracking/paid-media docs |

## Routing Rules

- If a task is about "what fires, when, and with which parameters", route it to conversion tracking.
- If a task is about "where the data lands and how it joins", route it to BigQuery/data.
- If a task is about "how pages are indexed or measured organically", route it to SEO.
- If a task is about "what campaigns/assets should be named", route it to naming convention.
- If a task is about "what ads should run or optimize against", route it to paid media.
- If a task is about "which school/program/location ID is canonical", route it to master data first, then link back to tracking or BigQuery.

## Required Handoff Style

Every substantial workstream update should include:

- Current verified status.
- What changed.
- What was tested or checked.
- What remains pending.
- Exact files updated.
- Whether live platform/backend writes were made.
