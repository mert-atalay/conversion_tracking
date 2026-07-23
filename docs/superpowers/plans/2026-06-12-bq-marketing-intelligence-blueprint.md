# CEFA BigQuery Marketing Intelligence Blueprint

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Evolve CEFA BigQuery from reliable dashboard reporting into a governed marketing intelligence engine for school, franchise, local/AEO, creative, predictive, and approved activation use cases.

**Architecture:** Supabase remains the operational CRM and parent/admissions system. BigQuery remains the marketing intelligence, measurement, semantic, predictive, and activation-prep warehouse. Existing dashboard contracts in `mart_cefa_growth_dashboard` stay stable while new sources enter as additive, QA-labeled contracts.

**Tech Stack:** BigQuery, Cloud Run, Cloud Scheduler, BigQuery Data Transfer Service, Dataform, Cloud Monitoring, Secret Manager, Cloud Storage, Pub/Sub or Cloud Tasks where needed, Dataplex/Knowledge Catalog, BigQuery ML, Gemini in BigQuery, Vertex AI only after BQ-native options are insufficient, Supabase safe exports, Hightouch for approved reverse ETL, GA4, Google Ads, Meta, GSC, GBP, DataForSEO, Gravity Forms, CRM lifecycle facts.

**Status:** Locked roadmap as of 2026-06-12. Future BQ, marketing intelligence, prediction, semantic layer, Hightouch, and Supabase bridge work should use this as the strategic roadmap unless Mert explicitly approves a replacement.

---

## Final Position

Use the new 2027 blueprint as direction, but do not rebuild the warehouse from scratch.

The right CEFA path is:

- preserve existing dashboard-safe objects and scheduled refreshes
- add the missing event, source, lifecycle, and semantic layers around them
- migrate orchestration toward Dataform gradually
- expose only certified contracts to dashboards, Supabase, Hightouch, and AI agents
- never copy raw parent/child PII into BigQuery semantic marts
- never let predictive or activation outputs change campaigns, budgets, CRM records, review replies, or public content without approval

The phrase "dual truth" should be used carefully. CEFA should not have two conflicting truths for the same metric. The split is:

- Supabase owns operational parent/admissions truth
- BigQuery owns marketing measurement and intelligence truth
- shared safe lifecycle facts connect the two systems

## What I Accept From The New Blueprint

- Form 4 should get a durable `event_id` before submission.
- Attribution fields, school context, click IDs, and source evidence should be captured first-party and sent to BigQuery.
- The existing Gravity Forms and KinderTales delivery path should remain untouched in the first pass.
- A Cloud Run collector is a good fit for webhook, browser-event audit, and future CAPI backup.
- Supabase should expose an `analytics_export` safe schema instead of giving BigQuery raw CRM tables.
- BigQuery should return clean scores, source context, and summaries back to Supabase, not raw marketing logs.
- Dataform should become the long-term transformation and testing layer.
- BigQuery ML/Gemini/Vertex should come after the facts and quality gates are stable.
- Hightouch should read approved BQ contracts only and act through approval gates.

## What I Would Modify

- Do not immediately create every proposed `cefa_*` dataset as a parallel warehouse. Map the concepts into current datasets first, then create new datasets only when isolation is useful.
- Do not move existing dashboard readers or Supabase syncs until replacements are reconciled and explicitly promoted.
- Do not start with full server-side GTM. Start with Form 4 event parity: browser event, webhook event, BQ event, GA4 generate_lead, and Meta CAPI backup.
- Do not treat Meta or Google platform conversions as final business CPL. Business CPL should use trusted spend divided by deduped, non-test, paid Form 4 or CRM-safe target leads.
- Do not run MMM until weekly source/lifecycle history is stable and annotated with business events.

## Phase 0 - Protect Current Truth

**Outcome:** Existing dashboard metrics remain stable while richer BQ work continues safely.

- [ ] Keep `mart_cefa_growth_dashboard` contracts unchanged unless a promotion is approved.
- [ ] Keep `dashboard_bq_monitor_latest`, Cloud Run safety monitor, and Codex control check active.
- [ ] Before every warehouse release, snapshot current school paid, franchise paid, CRM/forms, GA4, and QA totals.
- [ ] After every release, compare spend, leads, CPL, row counts, freshness, and dashboard-safe status.
- [ ] Document any dashboard-facing change before the dashboard agent consumes it.

## Phase 1 - Governance, Registry, And Metric Definitions

**Outcome:** Every table says what it is, whether it is safe, and what limitations it has.

- [x] Expand the contract registry for dashboard, intelligence, predictive, activation, and blocked/candidate contracts.
- [ ] Add or standardize fields: `data_through_date`, `last_loaded_at`, `source_systems`, `source_status`, `qa_status`, `dashboard_safe`, `predictive_safe`, `reconciliation_status`, `known_limitations`, `serving_contract_version`.
- [x] Create or formalize the metric registry for business CPL, paid leads, qualified leads, tours, enrollments, source quality, capacity opportunity, attribution confidence, creative fatigue, and AI visibility.
- [ ] Add Cloud Monitoring alerts for stale source dates, failed Cloud Run jobs, failed QA, and query/storage guardrail warnings.
- [ ] Keep Hightouch, Supabase, Vercel, and AI readers restricted to approved contracts.

Progress note, 2026-06-12: Day 0 governance/source dictionary implemented in `marketing-api-488017.cefa_governance` and documented in [Governance source dictionary, 2026-06-12](../../20-bigquery/governance-source-dictionary-2026-06-12.md). The remaining Phase 1 work is field standardization on source contracts, monitoring alerts, and consumer access enforcement.

## Phase 2 - Form 4 First-Party Event Foundation

**Outcome:** Parent inquiry tracking becomes event-based, deduped, and platform-reconcilable without changing the parent-facing submission flow.

- [ ] Add `event_id` generation before Form 4 submit.
- [ ] Capture hidden fields for UTM values, click IDs, landing URL, referrer, landing school slug, selected school slug, campaign target school slug, and consent state.
- [ ] Send Form 4 webhook to a Cloud Run collector while preserving the existing KinderTales delivery path.
- [ ] Write raw and normalized no-PII event audit rows to BigQuery.
- [ ] Add reconciliation tables for browser event, webhook event, GA4 generate_lead, Meta Pixel, and future Meta CAPI.
- [ ] Preserve cross-school inquiry flags instead of hiding them.

## Phase 3 - Native Source Gap Closure

**Outcome:** BQ stops relying only on inferred GBP/SEO/local evidence and starts ingesting direct source facts.

- [ ] Add native Google Business Profile performance by location/day: profile interactions, calls, direction requests, website clicks, searches, and school mapping.
- [ ] Add Google Search Console query/page/device/country daily facts for parent and franchise domains.
- [ ] Add DataForSEO rank, SERP, AI visibility, and technical SEO snapshots where useful and cost-safe.
- [ ] Add Google Ads native transfer coverage for campaign, ad group, keyword/search term, asset, and budget diagnostics where available.
- [ ] Continue Meta through the most reliable API/Supermetrics path, with campaign-level truth protected before creative/ad-set promotion.
- [ ] Add optional review/reputation ingestion only with human-approved review response workflow.

## Phase 4 - Supabase Safe Lifecycle Bridge

**Outcome:** BigQuery can measure lead quality, tours, enrollments, and capacity without becoming the CRM.

- [ ] Ask Supabase to expose safe `analytics_export` views for lifecycle events, stage snapshots, household identity tokens, capacity snapshots, consent status, and admissions activity.
- [ ] Ingest only safe lifecycle fields into BigQuery: lead ID, household ID, event ID, school UUID, stage, stage date, tour flags, enrollment flag, lost reason category, speed-to-lead bucket, consent state.
- [ ] Do not ingest parent names, child names, raw emails, raw phones, child DOB, street address, free-text CRM notes, or sensitive admissions comments.
- [ ] Build no-PII lifecycle facts that join to Form 4 and paid source evidence by `event_id`, `lead_id`, `household_id`, and `school_uuid`.
- [ ] Add capacity snapshots by school/month and mark unknown capacity as partial, not zero.

## Phase 5 - Core Facts And Semantic Marts

**Outcome:** Dashboards and analysts use stable business facts, not raw joins.

- [ ] Formalize canonical school identity: `school_uuid`, canonical slug, aliases, region, province, status, GBP place ID, website URL, inquiry URL, and reporting scope.
- [ ] Formalize campaign identity: platform, account, campaign ID/name, target school slug, lead type, objective, UTM campaign, status, and mapping confidence.
- [ ] Build or certify core facts for parent leads, touchpoints, CRM lifecycle events, campaign spend, creative performance, and capacity.
- [ ] Promote dashboard-safe marts only after reconciliation passes.
- [ ] Keep Supabase delivery tables small and final: school/day/campaign totals, source context, lead scores, message context, and approved recommendations.

## Phase 6 - Paid Media And Creative Reconciliation

**Outcome:** School drilldowns can explain performance by campaign, ad group, keyword, ad set, creative, and audience without distorting totals.

- [ ] Certify Google ad group totals against trusted campaign/school totals.
- [ ] Keep Google keyword/search term as engagement/search insight unless keyword-level conversion truth exists.
- [ ] Reconcile Meta ad set and creative spend/leads to trusted campaign totals before allowing CPL or spend ranking.
- [ ] Store creative metadata and URLs only; no creative binaries in BigQuery.
- [ ] Add Cloud Storage asset manifest, Cloud Vision OCR/labels, and Gemini theme labels after creative metadata QA passes.
- [ ] Build creative learning marts for fatigue, message themes, CTA, format, school context, and next-test recommendations.

## Phase 7 - Local, AEO, Reputation, And SEO Intelligence

**Outcome:** CEFA can understand local visibility and AI/search demand at the school level.

- [ ] Build semantic marts for GSC query/page opportunities.
- [ ] Build GBP/local performance scorecards by school.
- [ ] Build local reputation scorecards from reviews and response SLA, with human approval for any response workflow.
- [ ] Add AEO/AI visibility facts from DataForSEO/manual prompt tests where source access is stable.
- [ ] Convert these into school page, schema, content, and local listing opportunity backlogs.

## Phase 8 - Predictive Analytics V1

**Outcome:** BQ highlights what needs attention next, while recommendations remain advisory.

- [ ] Start with heuristic models already compatible with current BQ history.
- [ ] Add BigQuery ML models only when labels and history are strong enough: lead-to-tour propensity, enrollment propensity, no-show risk, school demand forecast, creative fatigue, anomaly detection.
- [ ] Store model metadata: model version, training window, features, confidence, limitations, scored date, expiry date.
- [ ] Compare predictions to actuals and track error before promotion.
- [ ] Push scores to Supabase only after business review and with expiry dates.

## Phase 9 - Dataform And Production Data Engineering

**Outcome:** Transformations become easier to test, debug, document, and release.

- [ ] Inventory current Cloud Run SQL scripts by source, staging, core, semantic, predictive, activation, and governance role.
- [ ] Move stable SQL transformations into Dataform incrementally, beginning with governance/source registry and semantic marts.
- [ ] Keep Cloud Run for source extraction, custom API calls, and backward-compatible refresh entrypoints.
- [ ] Add Dataform assertions for freshness, uniqueness, row count, spend reconciliation, lead reconciliation, and null safety.
- [ ] Add Dataplex/Knowledge Catalog descriptions after stable contracts are defined.

## Phase 10 - MMM And Incrementality Readiness

**Outcome:** Annual and quarterly budget planning becomes evidence-based rather than platform-report based.

- [ ] Build weekly MMM readiness table with spend, impressions, clicks, paid leads, qualified leads, tours, enrollments, capacity, seasonality, holidays, school openings, GBP actions, and organic clicks.
- [ ] Annotate major launches, tracking changes, creative refreshes, pauses, and website changes.
- [ ] Design simple holdout or pre/post tests before relying on model outputs.
- [ ] Use Meridian or another MMM path only after enough stable weekly history exists.

## Phase 11 - Controlled Activation

**Outcome:** Insights become action queues, not autonomous changes.

- [ ] Create recommendation queue with owner, source evidence, confidence, approval status, approved by, implemented at, and outcome tracking.
- [ ] Use Hightouch only on approved BigQuery contracts and its own audit/planner schemas.
- [ ] Start with Supabase reporting/score outputs before ad-platform activation.
- [ ] Add offline conversion, suppression, seed audience, and CAPI enrichment tables only after privacy and QA review.
- [ ] No automatic campaign, budget, bid, CRM, review, content, or public-site changes.

## Phase 12 - Agent-Safe Semantic Layer

**Outcome:** CEFA can ask natural-language questions over trusted marketing data safely.

- [ ] Create agent-safe views for school growth, campaign reconciliation, lead ops bottlenecks, creative learning, AEO opportunities, and local reputation.
- [ ] Ensure agent views expose definitions, freshness, QA state, and source contracts.
- [ ] Block raw table access for agents.
- [ ] Log agent runs, data scopes used, recommendations, approval status, and executed action if any.
- [ ] Require source citations and freshness timestamps in any executive summary or recommendation.

## Immediate Priority Order

1. Finish governance and metric registry so every next build has a contract.
2. Implement Form 4 `event_id` and Cloud Run collector as an additive audit path.
3. Add Supabase safe lifecycle export planning and schema agreement.
4. Add native GBP and GSC ingestion.
5. Load budget targets and campaign ops calendar.
6. Certify Google ad group/keyword and Meta ad set/creative detail.
7. Build capacity-aware school growth and lead-quality marts.
8. Move stable SQL into Dataform.
9. Upgrade predictive tables from heuristics to BQML where labels are mature.
10. Add Hightouch/activation only after recommendation records are approved and audited.

## Dashboard Agent Handoff

No current dashboard metrics should change from this plan by default.

The dashboard agent can safely continue consuming current `mart_cefa_growth_dashboard` contracts. New views should be consumed only when they are explicitly marked `dashboard_safe = true`, have passing QA, and have a handoff note that names the changed contract and expected UI behavior.

## Cost And Safety Guardrails

- Prefer daily aggregates and bounded feature tables over unlimited raw expansion.
- Keep raw event retention and partitioning rules explicit before high-volume sources are added.
- Run BQ usage guardrails after every major source addition.
- Add Cloud Vision, Gemini, Vertex AI, and MMM workloads only after source tables are stable and the expected monthly cost is approved.
- Keep all write-capable actions behind human approval.

## Non-Goals

- Do not replace Supabase as CRM.
- Do not copy raw parent/child PII into BigQuery.
- Do not replace Form 4 in the first pass.
- Do not break KinderTales delivery.
- Do not use platform conversions as final business CPL.
- Do not merge parent enrollment, open house, summer camp, franchise, and other lead types into one CPL bucket.
- Do not launch autonomous budget, CRM, creative, review, or publishing agents.
