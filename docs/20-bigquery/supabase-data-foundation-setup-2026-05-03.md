# Supabase Data Foundation Setup

Last updated: 2026-05-03

## Purpose

This document records the new Supabase project setup for the CEFA marketing measurement and data foundation work in this repo.

This is not a live schema migration. It defines the current verified setup, the intended database role, the first build order, and the gaps that must be resolved before writing production tables.

## Current Verified Setup

| Item | Current state | Status |
|---|---|---|
| Codex MCP server name | `supabase` | Verified |
| Supabase project ref | `twtfbvegbpwfzoaseezo` | Verified from configured MCP URL |
| MCP server URL | `https://mcp.supabase.com/mcp?project_ref=twtfbvegbpwfzoaseezo&features=account%2Cdocs%2Cdatabase%2Cdebugging%2Cdevelopment%2Cfunctions%2Cbranching%2Cstorage` | Verified |
| Enabled MCP features | `account`, `docs`, `database`, `debugging`, `development`, `functions`, `branching`, `storage` | Verified from configured MCP URL |
| Codex remote MCP support | `[mcp] remote_mcp_client_enabled = true` in `~/.codex/config.toml` | Verified |
| Codex MCP auth | `codex mcp login supabase` completed successfully; `codex mcp list` shows `Auth: OAuth` | Verified |
| Supabase MCP endpoint reachability | `curl https://mcp.supabase.com/mcp` returns `401` without auth, which means the hosted server is reachable | Verified |
| Local Supabase skill files | `.agents/skills/supabase` and `.agents/skills/supabase-postgres-best-practices` are present in this local worktree | Partial/local tooling |
| Supabase app/plugin connector | Installed connector currently sees the older project `jypxjqxpjztczijbpxeu`, not `twtfbvegbpwfzoaseezo` | Partial |
| Supabase CLI | Not installed on the local PATH during this setup pass | Missing |

## Important Tooling Boundary

The Codex MCP server and the installed Supabase plugin are not currently the same authenticated path.

| Tool path | Current behavior |
|---|---|
| Codex MCP `supabase` | Configured and OAuth-authenticated to project ref `twtfbvegbpwfzoaseezo`. The tools may require a Codex session refresh before they appear as callable tools in this thread. |
| Supabase plugin connector | Callable in this thread, but it only lists project `jypxjqxpjztczijbpxeu` and returns a permission error for `twtfbvegbpwfzoaseezo`. |

Do not assume plugin access proves the new project is unavailable. The Codex MCP config is authenticated, but this current thread may need reload/restart or `/mcp` verification before the new server tools are exposed.

The local Supabase skill files are tooling support only. Do not treat their presence or absence as proof that the new Supabase project is connected or disconnected.

## Intended Database Role

This Supabase project should be the clean CEFA data foundation, not a continuation of the older messy database.

Primary goals:

- Store raw source pulls separately from normalized reporting tables.
- Build canonical school, program, source, campaign, and metric dimensions.
- Reconcile Gravity Forms, GreenRope, WordPress/School Manager, GA4/BigQuery, Google Ads, Meta, Supermetrics, GBP, and future franchise data through stable IDs.
- Keep dashboards on normalized facts/marts, not direct raw imports.
- Keep AI/runtime/checkpoint logs out of the foundational database unless a separate retention policy is approved.

## Proposed Schema Layout

Use private schemas by default. Do not expose raw or PII-heavy tables through the public Data API.

| Schema | Purpose | Exposure rule |
|---|---|---|
| `raw` | Untouched source pulls from Gravity Forms, GreenRope, GA4/BigQuery exports, paid media, GBP, and School Manager snapshots. | Private; restrict PII access. |
| `stage` | Parsed and lightly cleaned source tables with source-specific IDs preserved. | Private. |
| `core` | Canonical dimensions and governed metric definitions. | Private by default; expose only approved read views if needed. |
| `mart` | Reporting-ready facts and dashboard views. | Private by default; expose selected views only after RLS/grants are explicit. |
| `ops` | Sync status, row counts, source coverage, error logs, mapping review queue. | Private or admin-only. |
| `audit` | Immutable sync/audit events and quality-check outputs. | Private. |

If any table or view is placed in an exposed schema, enable RLS and create explicit policies/grants that match the access model.

## First Build Order

| Step | Output | Status |
|---:|---|---|
| 1 | Verify project metadata, organization, region, database version, and current schema list through the refreshed Supabase MCP path. | Pending |
| 2 | Create repo-local Supabase migration workflow only after CLI/MCP write path is confirmed. | Pending |
| 3 | Create `core.dim_school` from the governed 53-school reference using `school_uuid` as the primary key. | Pending |
| 4 | Create `core.dim_program` from the governed program reference using `program_id` as the primary key. | Pending |
| 5 | Create `core.source_system`, `core.metric_definition`, and source-priority rules. | Pending |
| 6 | Create `ops.sync_run`, `ops.source_coverage_daily`, `ops.mapping_review_queue`, and `ops.data_quality_check`. | Pending |
| 7 | Add raw tables for Gravity Forms and GreenRope first. | Pending |
| 8 | Add normalized lead, paid-signal, tour, enrollment, spend, and availability snapshot facts. | Pending |
| 9 | Add marts for school/month, school/program/month, executive monthly, source coverage, and school current state. | Pending |
| 10 | Add selected writeback design for WordPress School Manager only after the availability bridge is reviewed. | Future |

## Initial Canonical Tables

| Table | Grain | Key fields |
|---|---|---|
| `core.dim_school` | One row per school | `school_uuid`, `school_slug`, `location_name`, `region`, `wordpress_school_manager_id`, `greenrope_group_id`, `gravity_location_id`, `gbp_location_id`, `school_code`, `canonical_location_id`, `status` |
| `core.dim_program` | One row per program | `program_id`, `program_key`, `program_name`, `program_family`, `is_waitlist`, `is_weekend_care`, `status` |
| `core.source_system` | One row per source | `source_system_id`, `source_name`, `source_owner`, `source_priority`, `contains_pii`, `status` |
| `core.metric_definition` | One row per metric | `metric_key`, `display_name`, `definition`, `source_priority`, `date_boundary`, `owner`, `status` |
| `ops.sync_run` | One row per sync attempt | `source_system_id`, `started_at`, `finished_at`, `status`, `row_count`, `error_message`, `source_cursor` |
| `ops.mapping_review_queue` | One row per unresolved mapping | `source_system_id`, `field_name`, `source_value`, `proposed_match`, `confidence`, `status`, `reviewed_by`, `reviewed_at` |
| `ops.source_coverage_daily` | Source + date | `source_system_id`, `date`, `rows_loaded`, `schools_mapped`, `schools_missing`, `latest_source_timestamp` |

## Raw Sources To Prioritize

| Priority | Raw source | Reason |
|---:|---|---|
| 1 | Gravity Forms Form 4 parent inquiries | Defines saved form submission truth and paid-signal fields. |
| 2 | GreenRope opportunities, contacts, activities, events, journeys | Defines CRM funnel state, tours, enrollments, lost-lead workflow, and operational context. |
| 3 | WordPress School Manager availability snapshots | Defines current website-facing school/program availability until automation is approved. |
| 4 | GA4 BigQuery export and marketing warehouse extracts | Validates tracking events and joins website behavior to school/program dimensions. |
| 5 | Google Ads, Meta, and Supermetrics feeds | Adds paid-media spend/conversion context after source IDs and school joins are stable. |
| 6 | GBP locations and reviews | Adds local listing and parent sentiment context, not funnel truth. |
| 7 | Parent Insights | Separate parent-experience domain; do not mix into lead/conversion truth. |

## Security And PII Rules

| Rule | Current decision |
|---|---|
| Secrets | No service role keys, OAuth tokens, passwords, or connection strings in repo docs. |
| Raw PII | Parent names, emails, phones, child DOB, notes, franchise contact details, and free text stay in restricted raw tables only. |
| Public Data API | Do not expose raw/stage tables. If any table/view is exposed, configure grants and RLS intentionally. |
| Views | Use security-aware view design; do not assume views enforce RLS by default. |
| Service role | Never use service-role keys in browser or public client code. |
| AI/runtime logs | Exclude by default from this foundation unless retention and PII policy are approved. |

## Current Open Questions

| Question | Why it matters |
|---|---|
| Which Supabase organization owns `twtfbvegbpwfzoaseezo`? | Needed before project-cost, billing, and ownership claims. |
| What is the project name, region, database version, and current schema list? | Must be verified through refreshed MCP tools before schema work. |
| Should the repo install and pin Supabase CLI locally, or rely on MCP-first migrations? | Determines migration workflow and local verification path. |
| Should this repo include a `supabase/` CLI project folder? | Useful for migrations/functions, but should be created through the CLI rather than guessed. |
| Which dashboard or app will read this Supabase project first? | Determines whether public API exposure is needed or whether admin-only/reporting access is enough. |
| What is the first live source to ingest: Gravity Forms or GreenRope? | Determines the first raw schema and sync-run contract. |

## Next Operational Step

Restart/reload Codex or run `/mcp` in the Codex UI to confirm the newly authenticated `supabase` MCP tools appear for project `twtfbvegbpwfzoaseezo`.

After that, run read-only introspection first:

```sql
select current_database(), current_user, version();
select schema_name from information_schema.schemata order by schema_name;
```

Only after the project is confirmed should we apply baseline DDL for schemas and canonical tables.
