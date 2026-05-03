# CEFA Master Data, Taxonomy, Conversion, And Metrics Reference

Last updated: 2026-05-03

## Purpose

This is the current master reference for the data sources, source ownership, taxonomy, conversion contracts, program reference, metric definitions, known gaps, and recommended clean data model available from the current CEFA local repositories and conversion-tracking documentation.

This document does not replace the narrower implementation docs. It points to them and consolidates the current working truth in one place.

Status labels used below:

| Status | Meaning |
|---|---|
| Verified | Confirmed by current docs, code, live audit notes, local reference files, or checked warehouse/API output. |
| Partial | Available, but incomplete, mixed-format, locally recoverable only, or not yet reconciled into one canonical table. |
| Pending | Known needed field, decision, access, or refresh dependency not confirmed yet. |
| Open question | Needs user, platform owner, agency, source-system, or business-owner confirmation. |
| Missing | Needed for the master model, but not available as a populated authoritative field today. |
| Reference only | Useful context, but not authoritative KPI truth. |
| Future | Valid architecture direction, but not part of the current stable source-of-truth layer. |

## Governance And Workstream Placement

This document belongs to `docs/60-master-data/`. It is the consolidated reference, not the only source of truth. Narrow implementation, platform, and QA facts should still live in their owning workstream folders and be linked here.

### Authority Order

| Priority | Source type | Rule |
|---:|---|---|
| 1 | Live verified systems | WordPress, Gravity Forms, GTM, GA4, Google Ads, Meta, BigQuery, CRM exports, browser/network proof, and current API output win over stale docs. |
| 2 | Runtime code and current governed docs | Use repo code and current docs for migrated, checked, and actively maintained facts. |
| 3 | Local CEFA conversion-tracking knowledge base | Use `/Users/matthewbison/Desktop/cefa-nexus/CEFA/cefa conversion tracking/` only for unmigrated evidence and cite it as source evidence. |
| 4 | CEFA local NEXUS context | Use `/Users/matthewbison/Desktop/cefa-nexus/CEFA/.agency/context/` as upstream context, not as the governed repo source when a current `docs/` file exists. |
| 5 | CEFA Ops vault/source files | Use only when explicitly cited and relevant to the active workstream. |
| 6 | External platform best practices | Reference only unless verified against CEFA's live configuration. |

### Workstream Routing

| Folder | Use |
|---|---|
| `docs/00-governance/` | Repo rules, source-of-truth hierarchy, contribution workflow, agent handoff standards, and repo map. |
| `docs/10-conversion-tracking/` | Parent/franchise tracking contracts, GTM/GA4/Ads/Meta mappings, event IDs, CAPI, sGTM, and Measurement Protocol decisions. |
| `docs/20-bigquery/` | Warehouse state, marts, SQL, row coverage, refresh jobs, Looker/reporting contracts, and offline conversion exports. |
| `docs/30-seo/` | SEO measurement, technical/local SEO, Search Console, page taxonomy, and SEO research handoffs. |
| `docs/40-naming-convention/` | Meta naming, creative filenames, GBP/Yelp UTM rules, and campaign/source naming governance. |
| `docs/50-paid-media/` | Platform launch QA, data availability, campaign/conversion use, optimization notes, and platform-owner decisions. |
| `docs/60-master-data/` | School, program, location, CRM, platform, and reporting crosswalks plus metric/source taxonomy. |

### Cross-Workstream Rule

Do not promote assumptions into this master document as verified truth. Use `Verified`, `Partial`, `Pending`, `Open question`, `Missing`, `Reference only`, and `Future` explicitly, and update the narrower owning document when a fact changes.

## Primary Rules

| Rule | Current decision | Status | Source pointers |
|---|---|---|---|
| Primary parent school join key | Use `school_uuid`, emitted as Form 4 `32.1` and helper payload `school_selected_id`. | Verified | `known-school-program-reference-table-2026-05-03.md`, `canonical-school-program-taxonomy-2026-05-03.md`, `README.md` |
| Primary parent program join key | Use `program_id`, emitted as Form 4 `32.2` and helper payload `program_id`. | Verified for observed programs | `known-school-program-reference-table-2026-05-03.md`, `canonical-school-program-taxonomy-2026-05-03.md` |
| Event identity | Use `event_id`, not school ID, program ID, slug, or label. | Verified | `phase1a/event-flow-and-lifecycle.md`, helper plugin code |
| Parent final conversion source | CEFA helper plugin dataLayer event `school_inquiry_submit`, mapped in GTM to GA4 `generate_lead` and paid platforms. | Verified | `parent-production-cutover-checklist.md`, `live-conversion-tracking-status-2026-05-01.md` |
| Gravity Forms Measurement Protocol | Audit-only first; do not send a second GA4 `generate_lead` while browser/GTM `generate_lead` is active. | Verified decision | `phase1b-measurement-protocol-server-side-options-2026-05-01.md` |
| School availability operational source | WordPress School Manager is the operational availability surface today; GreenRope is lead/journey context unless a clean school/program matrix is created. | Verified from prior live-source review, revalidate before writes | `/Users/matthewbison/Desktop/agentic-brain/docs/agent-notes/2026-05-03-school-program-known-vs-missing.md`, School Manager/GreenRope notes |
| Parent/franchise boundary | Parent enrollment, Franchise Canada, and Franchise USA are separate funnels and should not share optimization truth. | Verified | `cross-property-measurement-boundaries.md`, franchise phase docs |
| Labels | School labels, campaign names, slugs, and ad names are aliases only. Do not use them as final joins without stable IDs. | Verified | school/program taxonomy docs |

## Source Document Index

| Area | File / source | Use |
|---|---|---|
| Governed docs root | `docs/README.md` | Current entrypoint for the organized documentation layer and workstream routing. |
| Governance source-of-truth rules | `docs/00-governance/source-of-truth-rules.md` | Authority order, verification labels, stable decisions, and forbidden source swaps. |
| Governance repo map | `docs/00-governance/repo-map.md` | Where new docs belong and which areas must not be mixed. |
| Governance agent responsibilities | `docs/00-governance/agent-responsibilities.md` | Workstream ownership and required handoff format. |
| Governance contribution workflow | `docs/00-governance/contribution-workflow.md` | Required structure for dated docs, verification, and evidence. |
| Workstream update template | `docs/_templates/workstream-update-template.md` | Standard structure for new workstream update docs. |
| Plugin overview and contracts | `README.md` | Runtime ownership, parent/franchise dataLayer contracts, micro-events. |
| Business truth and tracking gaps | `docs/10-conversion-tracking/business-truth-and-tracking-data-gaps-2026-05-03.md` | Current business-truth gaps, stale marts, source reconciliation needs, and tracking-data limits. |
| BigQuery warehouse current state | `docs/20-bigquery/warehouse-current-state-2026-05-03.md` | Current warehouse refresh, view coverage, row counts, GA4 export range, paid-data freshness, and cost/tier usage. |
| Dashboard source layer and GreenRope aggregate | `docs/20-bigquery/dashboard-source-layer-greenrope-and-rule-registry-2026-05-03.md` | Dashboard service account, keyless auth path, GreenRope daily aggregate, CRM dashboard views, and measurement rule registry. |
| GreenRope metric definitions and API map | `docs/20-bigquery/greenrope-metric-definitions-and-api-map-2026-05-03.md` | Exact GreenRope metric definitions, loaded API endpoints, dashboard labels, and interpretation limits. |
| Supabase data foundation setup | `docs/20-bigquery/supabase-data-foundation-setup-2026-05-03.md` | New Supabase MCP setup, project boundary, schema plan, and first build sequence. |
| SEO restart handoff | `docs/30-seo/seo-restart-handoff-2026-05-03.md` | SEO measurement context, GSC/DataForSEO handoff, and SEO-only pending checks. |
| Final known school/program table | `docs/known-school-program-reference-table-2026-05-03.md` | 53 school rows, 6 program rows, canonical key guidance, known gaps. |
| Canonical taxonomy status | `docs/canonical-school-program-taxonomy-2026-05-03.md` | Cross-system taxonomy status, BigQuery evidence, recommended canonical tables. |
| Parent production state | `docs/parent-production-cutover-checklist.md` | Parent GTM/GA4/custom-dimension/cutover status. |
| Live conversion status | `docs/live-conversion-tracking-status-2026-05-01.md` | Parent, Franchise Canada, Franchise USA live conversion status. |
| Form and CRM integrity | `docs/live-form-crm-integrity-review-2026-04-30.md` | Live form submissions, Gravity Forms saved entries, CRM/Synuma proof. |
| Migration audit | `docs/live-migration-readonly-audit-2026-04-30.md` | Early live-domain read-only state and risks. |
| Phase 1A dataLayer | `docs/phase1a/datalayer-contract.md` | Parent final event and micro-event payload rules. |
| Phase 1A lifecycle | `docs/phase1a/event-flow-and-lifecycle.md` | Event ID lifecycle, token, reload, direct thank-you guard. |
| Phase 1A guardrails | `docs/phase1a/guardrails.md` | Duplicate and false-positive rules. |
| Plugin-vs-theme decision | `docs/phase1a/plugin-vs-theme-decision.md` | Ownership split between School Manager, helper plugin, and GTM. |
| Gravity Forms add-on decision | `docs/phase1a/gravity-forms-add-on-decision.md` | Why add-on is not the truth layer unless clean fields are proven. |
| Measurement Protocol | `docs/phase1b-measurement-protocol-server-side-options-2026-05-01.md` | Server-side/audit-only strategy. |
| Cross-property boundaries | `docs/cross-property-measurement-boundaries.md` | Parent vs Franchise Canada vs Franchise USA measurement separation. |
| Franchise Canada taxonomy | `docs/franchise-canada-phase1/02-event-taxonomy-and-datalayer-contract.md` | Franchise Canada form events, payloads, attribution fields, PII rules. |
| Franchise Canada QA | `docs/franchise-canada-phase1/05-qa-and-cutover-checklist.md` | Current Canada QA state and remaining platform confirmations. |
| Franchise USA QA/build | `docs/franchise-usa-phase1/01-gtm-build-and-qa-2026-05-01.md` and `02-qa-and-cutover-checklist.md` | USA GTM Version 15, helper mapping, remaining Ads/Meta confirmation. |
| Franchise USA post-Version-15 QA | `docs/franchise-usa-phase1/03-post-version-15-qa-2026-05-03.md` | Current USA form URLs, helper events, browser-level GA4 evidence, old 404 paths, and remaining Ads/Meta/GA4 reporting gaps. |
| Franchise implementation roadmap | `docs/franchise-transition-final-pack-v1/11-implementation-roadmap-and-build-board.md` | Existing workstream roadmap for parent cutover, franchise stabilization, USA setup, and Phase 1B/2. |
| CAPI and sGTM roadmap | `docs/franchise-transition-final-pack-v1/09-capi-and-sgtm-roadmap.md` | Existing long-term server-side, CAPI, and sGTM sequencing. |
| Parent local-listing UTM rules | `docs/40-naming-convention/local-listing-utm-rules-gbp-yelp-2026-05-03.md` | Governed GBP/Yelp parent-school local-listing UTM convention and reporting interpretation. |
| Paid-media data availability | `docs/50-paid-media/platform-data-availability-2026-05-03.md` | Current platform transfer status, row freshness, and paid-media use limitations. |
| School dimension warehouse coverage | `docs/60-master-data/school-dimension-warehouse-coverage-2026-05-03.md` | 53-school warehouse coverage, current view row counts, source coverage by platform, and external-ID gaps. |
| Agentic Brain source ownership | `/Users/matthewbison/Desktop/agentic-brain/docs/DASHBOARD_SOURCE_OWNERSHIP_MATRIX.md` | Current dashboard source ownership by surface and metric. |
| Agentic Brain metric contract | `/Users/matthewbison/Desktop/agentic-brain/docs/CRM_LEAD_CALCULATION_CONTRACT.md` | CRM lead calculation and dedupe rules. |
| Agentic Brain operational layer | `/Users/matthewbison/Desktop/agentic-brain/docs/CEFA_OPERATIONAL_LAYER_REFERENCE.md` | Reporting vs workflow vs engagement layer separation. |
| Agentic Brain CRM taxonomy | `/Users/matthewbison/Desktop/agentic-brain/docs/CRM_TAXONOMY_AND_CAPABILITY_REFERENCE.md` | GreenRope object families, endpoints, and limits. |
| Agentic Brain school/program note | `/Users/matthewbison/Desktop/agentic-brain/docs/agent-notes/2026-05-03-school-program-known-vs-missing.md` | Corrected local cross-system coverage and clean Supabase starting model. |

## Implementation And Local Data File Index

| Area | File / table | Current use |
|---|---|---|
| Helper plugin form contracts | `includes/class-cefa-conversion-tracking-config.php` | Hostname-scoped parent/franchise form IDs, field maps, attribution maps, static payload values. |
| Helper plugin payload builder | `includes/class-cefa-conversion-tracking-datalayer-payload.php` | Builds clean dataLayer payloads from saved Gravity Forms entries. |
| Helper plugin browser bridge | `assets/js/cefa-conversion-tracking.js` | Final event consumption, duplicate guards, micro-events, form-start/submit/validation signals. |
| Helper plugin event ID lifecycle | `includes/class-cefa-conversion-tracking-event-id.php` | Ensures/persists `event_id` for parent field `32.4` and franchise entry meta. |
| Helper plugin duplicate guard | `includes/class-cefa-conversion-tracking-duplicate-guard.php` | One-time payload token and consumed-event logic. |
| Franchise fallback bridge | `snippets/franchise-wpcode-bridge.php` | Live WPCode fallback bridge for franchise forms when full plugin deployment is blocked. |
| GreenRope local school map | `/Users/matthewbison/Desktop/agentic-brain/src/config/greenrope-group-map.ts` | Locally recoverable GreenRope group mapping for all 53 current schools, pending live CRM production validation. |
| BigQuery GreenRope bridge | `marketing-api-488017.mart_marketing.bridge_greenrope_group_school` | Loaded school-to-GreenRope group bridge. Duplicate group `50` is not dashboard-safe for automatic school totals. |
| BigQuery GreenRope daily aggregate | `marketing-api-488017.mart_marketing.fct_greenrope_school_funnel_daily` | Counts-only GreenRope daily group aggregate from `GetOpportunitiesRequest`; no full lead/contact payloads. |
| Gravity inquiry routing | `/Users/matthewbison/Desktop/agentic-brain/data/inquiry-location-forms.json` | Local Gravity routing/location code reference, currently 49/53 mapped. |
| GBP location export | `/Users/matthewbison/Desktop/agentic-brain/data/gbp-locations.json` | Local GBP reference, currently 47/53 mapped. |
| Local school ops snapshot | `/Users/matthewbison/Desktop/agentic-brain/data/schools.json` | Local school/program/enrollment context, reference only until reconciled to `school_uuid`. |
| Budget/ad token files | `/Users/matthewbison/Desktop/agentic-brain/data/budgets.json`, `/Users/matthewbison/Desktop/agentic-brain/data/campaign-budgets.json` | Local budget and partial ad-naming reference. |
| CRM lead calculation | `/Users/matthewbison/Desktop/agentic-brain/src/modules/school-ops/crm-reconciliation.ts` | Canonical CRM lead dedupe implementation. |
| Monthly materialization | `/Users/matthewbison/Desktop/agentic-brain/src/modules/school-ops/monthly-metrics-materializer.ts` | Monthly school/program metric persistence and rollups. |
| Executive/school analytics API | `/Users/matthewbison/Desktop/agentic-brain/src/api/routes/analytics.ts` | V2 executive/school metric assembly and source-labeled fallbacks. |
| BigQuery school dimension | `marketing-api-488017.mart_marketing.dim_school` | Current checked 53-row school dimension. |
| BigQuery empty core tables | `marketing-api-488017.cefa_core.dim_school`, `marketing-api-488017.cefa_core.dim_school_alias` | Schemas exist but are empty in checked evidence. |
| BigQuery assertion surface | `marketing-api-488017.dataform_assertions.assert_dim_school_location_not_null` | Assertion/failure surface; proves expected bridge columns exist, but not populated master values. |
| BigQuery GA4 export | `marketing-api-488017.analytics_267558140.events_*` | Parent GA4 event evidence and observed program IDs. |
| BigQuery marketing context fact | `marketing-api-488017.mart_marketing.fact_school_marketing_context_daily` | Current daily school marketing context fact; latest checked coverage has 53 schools per day. |
| BigQuery dashboard view | `marketing-api-488017.mart_marketing.vw_school_marketing_dashboard_daily` | Current dashboard-serving marketing view, populated through 2026-05-02 in the latest governed warehouse note. |
| BigQuery dashboard CRM view | `marketing-api-488017.mart_marketing.vw_school_marketing_dashboard_with_crm_daily` | Dashboard daily source with GreenRope aggregate fields joined only where the CRM group mapping is dashboard-safe. |
| BigQuery GreenRope school view | `marketing-api-488017.mart_marketing.vw_greenrope_school_funnel_school_daily` | School-level GreenRope aggregate view over the bridge and counts table. |
| BigQuery Looker contract view | `marketing-api-488017.mart_marketing.vw_school_marketing_looker_contract_daily` | Current Looker/reporting contract view, populated through 2026-05-02 in the latest governed warehouse note. |
| BigQuery measurement rule registry | `marketing-api-488017.cefa_core.measurement_rule_registry` and `mart_marketing.vw_measurement_rule_registry_current` | Dashboard-readable conversion-tracking and naming-convention rule references. Seeded with 5 current rows. |

## Data Source Registry

### Parent Enrollment And School Inquiry Sources

| Source | Owner / system | What it owns | Current status | Notes / gaps |
|---|---|---|---|---|
| WordPress `cefa.ca` | Website runtime | Parent inquiry pages, thank-you route, plugin runtime, School Manager output. | Verified | Current inquiry path is `/submit-an-inquiry-today/?location=<school-slug>`. |
| CEFA School Manager | WordPress plugin/runtime | School/program/day rendering, Field 32 custom compound behavior, school locking, availability surface. | Verified operational surface | Do not let tracking plugin overwrite business fields. Availability automation should write here only after structured bridge validation. |
| Gravity Forms Form 4 | WordPress/Gravity Forms | Saved parent inquiry entry, Form 4 field values, source submission record. | Verified | Form 4 is the parent inquiry form. Saved entry is the source behind the confirmed browser event. |
| Form 4 Field 32 | School Manager/Gravity Forms | School/program/day/event metadata. | Verified | Subfields: `32.1` school UUID, `32.2` program ID, `32.3` days per week, `32.4` event ID, `32.5` school slug, `32.6` school name, `32.7` program name. |
| Form 4 Fields 35-46 | CEFA attribution bridge | Parent attribution handoff. | Verified | `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`, `gclid`, `gbraid`, `wbraid`, `fbclid`, `msclkid`, `first_landing_page`, `first_referrer`. |
| CEFA Conversion Tracking plugin | CEFA helper plugin | Clean final dataLayer event, event ID lifecycle, duplicate/false-positive guards, attribution backfill. | Verified | Current parent live plugin path uses `school_inquiry_submit` after confirmed submission. |
| GTM parent container | CEFA/GTM | Maps neutral website events to GA4, Google Ads, Meta. | Verified | Active parent container: `GTM-NZ6N7WNC`; old `GTM-PPV9ZRZ` is reference-only/not present in sampled live HTML. |
| GA4 parent property | Google Analytics | Parent analytics and `generate_lead` reporting. | Verified | Property `267558140` / `Main Site - GA4`. Helper-plugin parent custom dimensions are registered. |
| BigQuery GA4 export | Google/BigQuery | Event-level GA4 export for helper events and historical legacy events. | Verified | Used for program evidence and helper-plugin generate_lead checks. |
| GA4 Data API runtime access | Google Analytics API | Non-BigQuery GA4 reporting/API path. | Pending | Service-account/runtime API access is not yet the reliable business-truth path; warehouse uses native GA4 export where available. |
| GreenRope CRM | CRM | Opportunities, phases, activities, contacts, journeys, workflow and engagement context. | Verified for CRM objects, partial for live availability | Strong for current funnel and workflow diagnostics. Not a clean live school/program availability matrix today. |
| GreenRope BigQuery aggregate | BigQuery / GreenRope API | Daily CRM opportunity counts by GreenRope group. | Verified aggregate; partial business interpretation | Loaded 6,390 group-date rows from 52 groups and 24,916 counted opportunities for 2025-06-12 through 2026-05-03. Stores counts only. `greenrope_ad_attributed_inquiries` means UTM/click-id evidence, not solid paid-media truth. |
| KinderTales | Business delivery / school identity | Current school unique ID appears to be `school_uuid`. | Partial | Treat `kindertales_school_id = school_uuid` unless downstream proves a separate ID. |

### Marketing, Paid Media, And Visibility Sources

| Source | Owner / system | What it owns | Current status | Notes / gaps |
|---|---|---|---|---|
| `marketing-api-488017.mart_marketing.dim_school` | BigQuery marketing mart | 53-row school/location dimension. | Verified | Has `school_uuid`, `canonical_location_id`, `location_code`, `location_name`, `school_slug`, `timezone`, `landing_page_path`. |
| `canonical_location_id` | BigQuery marketing mart | Current location metadata. | Partial | Present for all 53 schools, but mixed-format: 40 UUID-like and 13 slug-like. Do not use as main tracking join until normalized. |
| `mart_marketing.fact_school_marketing_context_daily` | BigQuery marketing mart | Daily school marketing context by school. | Verified | Latest governed check shows 12,084 rows and 53 schools. |
| `vw_school_marketing_dashboard_daily` | BigQuery marketing mart | Dashboard-serving daily marketing view. | Verified | Populated from 2025-09-17 through 2026-05-02 in the latest governed check. |
| `vw_school_marketing_dashboard_with_crm_daily` | BigQuery marketing mart | Dashboard-serving daily marketing view with GreenRope aggregate fields. | Verified | Queryable by the dashboard service account. GreenRope fields are joined only for dashboard-safe mappings. |
| `vw_school_marketing_looker_contract_daily` | BigQuery marketing mart | Looker/reporting contract view. | Verified | Latest governed check shows 80,678 rows and 53 schools. |
| `cefa-dashboard-bq-reader` service account | Google Cloud / BigQuery | Dashboard read identity. | Verified | Has project `roles/bigquery.jobUser` and dataset read access on `mart_marketing` and `cefa_core`. No service-account key was created. |
| `cefa_core.measurement_rule_registry` | BigQuery core | Current dashboard-facing conversion-tracking and naming-convention rule references. | Verified seeded surface | Current mart view exposes 5 active/current rows. This is a rule-reference registry, not permission to change CEFA NC1 naming. |
| Google Ads | Paid media | Google spend, clicks, conversion actions, linked Ads accounts. | Partial | Transfer config is enabled and recent runs succeeded, but checked campaign/conversion detail rows stop at 2026-04-30. School-level ad naming tokens are incomplete. |
| Meta Ads / Pixel | Paid media | Meta events, Lead/custom events, campaign reporting. | Partial | Native Meta rows are present through 2026-05-02, but May 1/2 dashboard paid metrics are zero in the latest governed check. Canada franchise currently verified on shared pixel `918227085392601`; separation is target architecture. |
| Supermetrics / reporting connectors | Marketing data movement | Paid-media reporting feeds and conversion action reporting. | Partial | Useful for reporting; latest checked Google/Meta Supermetrics detail stops at 2026-04-30 and is not sufficient alone for all Ads admin configuration. |
| GBP | Google Business Profile | Location visibility, reviews, GBP location IDs, scorecards. | Partial | Local GBP export maps 47/53 school locations. Six GBP gaps remain. |
| PiinPoint | Market intelligence | School/location market context. | Missing as deterministic key | App has fallback behavior, but populated `piinpoint_school_key` is not available in checked identity bridge. |
| Budget files | Local repo reference | Budget/spend planning and some school-level ad tokens. | Partial/reference | `data/budgets.json`, `data/campaign-budgets.json`. Only 15/53 schools currently have local budget-file ad tokens. |

### BigQuery Warehouse And Business-Truth Snapshot

| Area | Current verified state | Status | Notes / gaps |
|---|---|---|---|
| Warehouse refresh | Cloud Scheduler is enabled daily at `0 6 * * *` America/Vancouver; latest documented manual Cloud Run job completed on 2026-05-03. | Verified | Next documented scheduler run was 2026-05-04 13:00 UTC. Recheck live scheduler before making current-day claims after that date. |
| Dashboard auth | Dashboard reader identity `cefa-dashboard-bq-reader@marketing-api-488017.iam.gserviceaccount.com` exists and can query the dashboard CRM view. | Verified | Preferred production pattern is keyless Cloud Run service identity or Workload Identity Federation, not browser-side credentials. |
| Dashboard and Looker coverage | Core dashboard, dashboard-with-CRM, and Looker contract views are populated through 2026-05-02 with all 53 schools in latest seven-day context coverage. | Verified | May 1/2 paid values are partial/zero for some sources. |
| GreenRope daily aggregate | `mart_marketing.fct_greenrope_school_funnel_daily` contains 6,390 daily group rows from 2025-06-12 through 2026-05-03. | Verified aggregate; partial business interpretation | First load was manual. It stores counts only and exposes ad-attributed inquiry evidence, not platform-confirmed paid inquiries. |
| Measurement rule registry | `cefa_core.measurement_rule_registry` has 5 seeded conversion-tracking/naming-convention rule references exposed through `vw_measurement_rule_registry_current`. | Verified seeded surface | Future rule uploads still need a repeatable controlled workflow. |
| Native GA4 export | `analytics_267558140.events_*` is available from 2026-03-11 through 2026-05-02 in the governed check. | Verified | Use as event evidence, not as final business lead truth by itself. |
| Parent inquiry business-truth marts | `fct_parent_inquiries_daily` and `fct_parent_inquiries_by_location_daily` exist, but max at 2026-03-29. | Partial/stale | Must be refreshed before MTD/YTD stakeholder reporting depends on them. |
| Franchise lead-source mart | `fct_franchise_lead_sources_daily` exists but maxes at 2026-03-29 in checked evidence. | Partial/stale | Needs refresh and reconciliation before final franchise lead-source reporting. |
| Google Ads warehouse detail | Transfer config enabled and recent runs succeeded; checked campaign/conversion detail rows stop at 2026-04-30. | Partial | Current Google paid reporting after 2026-04-30 needs refresh/proof before claims. |
| Meta warehouse detail | Native Meta rows are present through 2026-05-02, while Supermetrics action/ad-set detail stops at 2026-04-30. | Partial | May 1/2 dashboard paid metrics are zero and need source-level explanation. |
| BigQuery free-tier usage | Latest governed check after dashboard/GreenRope/rule-registry work: May query usage 12.9346 GiB, about 1.263% of 1 TiB; storage 0.9679 GiB, about 9.68% of 10 GiB. | Verified snapshot | Snapshot only; recheck before billing/capacity decisions. |

### SEO Measurement Sources

| Source | Owner / system | What it owns | Current status | Notes / gaps |
|---|---|---|---|---|
| Google Search Console | SEO/search reporting | Organic search query/page performance. | Partial/stale snapshot | Current governed SEO handoff references data through 2026-03-31; refresh before current SEO claims. |
| DataForSEO artifacts | SEO research | Sector keyword, local/organic research, and SERP context. | Partial/reference | Existing artifacts are useful research inputs, not conversion or business-truth sources. |
| GBP SEO/category checks | Local SEO | Local listing category and profile optimization evidence. | Pending | Needs dedicated current verification before acting on listing/category recommendations. |

### Franchise Sources

| Source | Owner / system | What it owns | Current status | Notes / gaps |
|---|---|---|---|---|
| `franchise.cefa.ca` | Franchise Canada website | Canada franchise forms and thank-you pages. | Verified live tracking path | Uses WPCode fallback bridge and `GTM-TPJGHFS`. |
| `franchisecefa.com` | Franchise USA website | USA franchise forms and thank-you pages. | Verified website/GTM path; reporting still pending | Production form URLs are live on `/available-opportunities/franchising-inquiry/` and `/partner-with-cefa/real-estate-partners/submit-a-site/`; old `/franchise-application/` and `/real-estate-submission/` paths now return 404. Uses WPCode fallback bridge and `GTM-5LZMHBZL` Version 15 GA4 helper mapping. Ads/Meta final mapping still needs USA-specific confirmation. |
| Gravity Forms Franchise Form 1 | Franchise sites | Franchise Inquiry. | Verified | Event `franchise_inquiry_submit`; Form 1 field IDs differ from parent. |
| Gravity Forms Franchise Form 2 | Franchise sites | Real Estate / Site Inquiry. | Verified | Event `real_estate_site_submit`. |
| GAConnector fields 14-30 | Franchise forms | Last-click, first-click, click/client attribution. | Partial/verified in some Canada runtime tests | Do not overwrite. Canada field population is stronger than the first read-only audit; USA still needs final confirmation. |
| Synuma/SiteZeus/CEFA Franchise API | Franchise CRM delivery | Franchise downstream CRM and lead delivery. | Verified at saved-entry/meta level for tested submissions | Delivery can be delayed; do not treat immediate absence of `cefa_synuma_lead_id` as final failure without recheck. |

### Reporting And Operational Sources

| Source | Owner / system | What it owns | Current status | Notes / gaps |
|---|---|---|---|---|
| BI workbook / reporting layer | BI / workbook import | Monthly history, reporting comparisons, school operations, waitlisted, occupancy-style enrollment percentage. | Reference only / partial | Useful for reporting context, not the same as canonical CRM funnel truth. |
| Agentic Brain V2 executive/school APIs | CEFA Brain | Canonical/reconciled dashboard surfaces. | Verified current product surface | Uses canonical CRM first with source-labeled fallbacks. |
| CRM workflow aggregates | GreenRope/Agentic Brain | Workflow/activity diagnostics and operator burden. | Verified explanatory layer | Activities, journeys, email and events explain pipeline behavior but do not replace reporting totals. |
| Parent Insights | Chatbot / semantic analytics | Chat sessions, sentiment, readiness, knowledge gaps, reviews fallback. | Separate domain | Not a lead/conversion source of truth. |

## School Identity Taxonomy

### Current Coverage

| Field | Coverage | Status | Master rule |
|---|---:|---|---|
| `school_uuid` | 53/53 | Verified | Use as primary parent tracking school key. |
| `kindertales_school_id` | 53/53 as `school_uuid` | Partial | Keep separate only if downstream proves another KinderTales ID. |
| `canonical_location_id` | 53/53 | Partial | Known but not normalized: 40 UUID-like, 13 slug-like. |
| `location_code` | 53/53 | Verified | Alias/routing token, not the main join key. |
| `location_name` | 53/53 | Verified | Display label, not a join key. |
| `region` | 53/53 | Verified | Province/operating region. |
| `school_code` | 50/53 | Partial | Missing for three schools. |
| `school_slug` | 53/53 | Verified | Website/path alias. |
| `landing_page_path` | 53/53 | Verified | Website/path alias. |
| WordPress School Manager ID | 51/53 locally known | Partial | Two gaps remain. |
| GreenRope group/location ID | 53/53 loaded to BigQuery bridge | Partial | Locally reconciled from `agentic-brain` and loaded to `bridge_greenrope_group_school`; duplicate group `50` maps to two South Surrey rows, so only one-school mappings are dashboard-safe. |
| Gravity location ID/code/routing | 49/53 locally known | Partial | Four routing gaps remain. |
| GBP location ID | 47/53 locally known | Partial | Six GBP gaps remain. |
| School-level ad token | 15/53 locally known | Partial | Need platform export or naming owner confirmation. |
| `piinpoint_school_key` | 0/53 populated in checked bridge | Missing | Deterministic bridge key needed or keep PiinPoint as non-authoritative fallback. |

### Canonical Location Normalization Worklist

These 13 `canonical_location_id` values are present but slug-like. They need normalization or explicit approval before `canonical_location_id` becomes a cross-system join key.

| School | Current `canonical_location_id` |
|---|---|
| Burnaby - Brentwood | `burnaby-brentwood` |
| Burnaby - Canada Way | `burnaby-canada-way` |
| Calgary - Beacon Hill | `calgary-beacon-hill` |
| Calgary - South | `calgary-south` |
| Delta - Captains Cove | `delta-captain-s-cove` |
| New Westminster Downtown | `new-westminster-downtown` |
| Richmond - Crestwood | `richmond---crestwood` |
| South Surrey - Morgan Crossing | `morgan-crossing` |
| Surrey - Cloverdale | `surrey-cloverdale` |
| Surrey - Panorama North | `surrey---panorama-north` |
| Surrey - Sullivan Ridge | `sullivan-ridge` |
| Vancouver - Commercial Drive | `vancouver-commercial-drive` |
| Victoria - Douglas | `victoria---douglas` |

### Remaining School Identity Gaps

| Gap type | Missing rows |
|---|---|
| WordPress School Manager ID | South Surrey - Morgan Crossing East; Surrey - Panorama North |
| Gravity routing | South Surrey - Morgan Crossing East; Surrey - Cloverdale; Surrey - Panorama North; Surrey - Sullivan Ridge |
| GBP location ID | Calgary - Northland; Langley - Willowbrook; Richmond - Crestwood; Surrey - Panorama North; Vancouver - Kitsilano; Victoria - Douglas |
| School code | Calgary - South; North Vancouver - Capilano Mall; Surrey - Sunnyside |
| PiinPoint deterministic key | All 53 currently missing as populated bridge keys |
| Ad naming token | 38/53 not represented in current local budget files |
| Duplicate GreenRope group mapping | Group `50` maps to both South Surrey - Morgan Crossing and South Surrey - Morgan Crossing East; do not split or add those CRM totals without a business decision |

## Program Reference

Current verified program values come from recent live GA4 BigQuery `generate_lead` rows where `tracking_source=helper_plugin`, backed by Form 4 fields `32.2=program_id` and `32.7=program_name`.

| program_id | program_key | program_name | Aliases | Status |
|---|---|---|---|---|
| `411` | `baby` | CEFA Baby | Baby; CEFA Baby | Verified observed |
| `475` | `jk1` | Junior Kindergarten 1 | JK1; Junior Kindergarten 1 | Verified observed |
| `478` | `jk2` | Junior Kindergarten 2 | JK2; Junior Kindergarten 2 | Verified observed |
| `482` | `jk3` | Junior Kindergarten 3 | JK3; Junior Kindergarten 3 | Verified observed |
| `486` | `weekend_care` | CEFA Weekend Care Program | Weekend Care; CEFA Weekend Care; CEFA Weekend Care Program | Verified observed |
| `2030` | `waitlist` | Waitlist | Waitlist | Verified observed, needs modeling decision |

Program modeling decisions still needed:

| Decision | Current position |
|---|---|
| Should Waitlist be a program, a status, or both? | Not finalized. Keep row for observed tracking, but model carefully. |
| Should Weekend Care be a standard program or supplemental category? | Not finalized. Keep as observed program row for now. |
| CRM/KinderTales journey-code mapping to programs and availability states | Missing. Needs CRM/KinderTales source confirmation. |
| Program family taxonomy | Needed. Proposed families: `early_learning`, `weekend_care`, `waitlist/status`. |

## Conversion Event Taxonomy

### Parent Canada

| Event | Scope | Source | Destination mapping | Status |
|---|---|---|---|---|
| `school_inquiry_submit` | Primary conversion | CEFA helper plugin after confirmed Form 4 success | GA4 `generate_lead`, Google Ads parent conversion, Meta `Lead` | Verified |
| `parent_inquiry_cta_click` | Micro | Browser helper plugin | GA4 diagnostic/reporting | Verified |
| `find_a_school_click` | Micro | Browser helper plugin | GA4 diagnostic/reporting | Verified |
| `phone_click` | Micro | Browser helper plugin | GA4 diagnostic/reporting; existing GA4 key event exists | Verified |
| `email_click` | Micro | Browser helper plugin | GA4 diagnostic/reporting; existing GA4 key event exists | Verified |
| `form_start` | Micro | Browser helper plugin | GA4 diagnostic/reporting | Verified |
| `form_submit_click` | Micro | Browser helper plugin | GA4 diagnostic/reporting only | Verified |
| `validation_error` | Micro/diagnostic | Browser helper plugin after failed validation render | GA4 diagnostic/reporting, not key event | Verified |
| `school_inquiry_submit_server_audit` | Server audit | Future GF MP or CEFA plugin/collector | GA4 audit only, not key event | Future/audit-only |

Parent final event required payload fields:

| Field | Meaning | Source |
|---|---|---|
| `event` | `school_inquiry_submit` | Helper plugin |
| `event_id` | Same as Form 4 `32.4` | Gravity Forms / helper plugin |
| `form_id` | `4` | Static payload |
| `form_family` | `parent_inquiry` | Static payload |
| `lead_type` | `cefa_lead` | Static payload |
| `lead_intent` | `inquire_now` | Static payload |
| `school_selected_id` | School UUID | Field `32.1` |
| `school_selected_slug` | School slug | Field `32.5` |
| `school_selected_name` | School display label | Field `32.6` |
| `program_id` | Program ID | Field `32.2` |
| `program_name` | Program label | Field `32.7` |
| `days_per_week` | Days selected | Field `32.3` |
| `inquiry_success` | Confirmed success boolean | Helper plugin |
| `tracking_source` | `helper_plugin` | Helper plugin |

### Franchise Canada

| Event | Scope | Form | Destination mapping | Current status |
|---|---|---:|---|---|
| `franchise_inquiry_submit` | Primary conversion | Form 1 | GA4 `generate_lead`, Google Ads Canada inquiry action, Meta custom/Lead event, LinkedIn | Verified in live browser/network evidence |
| `real_estate_site_submit` | Primary conversion | Form 2 | GA4 `generate_lead` or split event, Google Ads site inquiry action, Meta custom/Lead event, LinkedIn | Verified in live browser/network evidence |
| `cefa_franchise_inquiry_dispatch` | GTM dispatch | Form 1 | Dispatch layer before destination tags | Verified |
| `cefa_real_estate_site_dispatch` | GTM dispatch | Form 2 | Dispatch layer before destination tags | Verified |
| Franchise micro-events | Micro | Forms/pages | GA4 diagnostic/reporting | Planned/partial |

Franchise Canada key payload fields:

| Field | Meaning |
|---|---|
| `site_context` | `franchise_ca` |
| `business_unit` | `franchise` |
| `market` | `canada` |
| `country` | `CA` |
| `form_family` | `franchise_inquiry` or `site_inquiry` |
| `lead_type` | `franchise_lead` or `real_estate_lead` |
| `lead_intent` | `franchise_inquiry` or `submit_a_site` |
| `location_interest` | Form 1 field `32`, non-PII categorical value |
| `investment_range` | Form 1 field `7` |
| `opening_timeline` | Form 1 field `10` |
| `school_count_goal` | Form 1 field `11` |
| `ownership_structure` | Form 1 field `12` |
| `site_offered_by` | Form 2 field `39` |
| `property_square_footage_range` | Form 2 field `34` |
| `outdoor_space_range` | Form 2 field `35` |
| `availability_timeline` | Form 2 field `36` |

### Franchise USA

| Event | Scope | Form | Destination mapping | Current status |
|---|---|---:|---|---|
| `franchise_inquiry_submit` | Primary conversion | Form 1 | GA4 `generate_lead` in USA property | Verified website/helper event in post-Version-15 controlled QA; processed GA4 reporting still pending after delay |
| `real_estate_site_submit` | Primary conversion | Form 2 | GA4 `generate_lead` in USA property | Verified website/helper event and browser-level GA4 hit in post-Version-15 controlled QA; processed GA4 reporting still pending after delay |
| `cefa_franchise_us_inquiry_dispatch` | GTM dispatch | Form 1 | USA GA4 helper dispatch | Verified in live `gtm.js` and controlled QA |
| `cefa_franchise_us_site_dispatch` | GTM dispatch | Form 2 | USA GA4 helper dispatch | Verified in live `gtm.js` and controlled QA |

USA post-Version-15 QA facts:

| Fact | Current state |
|---|---|
| Form 1 production URL | `https://franchisecefa.com/available-opportunities/franchising-inquiry/`, HTTP 200, `GTM-5LZMHBZL` and WPCode bridge markers present. |
| Form 2 production URL | `https://franchisecefa.com/partner-with-cefa/real-estate-partners/submit-a-site/`, HTTP 200, `GTM-5LZMHBZL` and WPCode bridge markers present. |
| Old test paths | `/franchise-application/` and `/real-estate-submission/` return 404. |
| Controlled Form 1 event | `franchise_inquiry_submit` with dispatch `cefa_franchise_us_inquiry_dispatch`; `location_interest=1190`; `site_context=franchise_us`, `market=usa`, `country=US`, `form_id=1`. |
| Controlled Form 2 event | `real_estate_site_submit` with dispatch `cefa_franchise_us_site_dispatch`; browser resource evidence showed GA4 request to `G-YL1KQPWV0M` with `generate_lead`, value `250`, currency `USD`; `site_context=franchise_us`, `market=usa`, `country=US`, `form_id=2`. |
| Processed GA4 reporting | Property `519783092` had no processed `generate_lead` rows yet in the documented follow-up; treat reporting confirmation as pending until rechecked after processing delay. |
| USA Google Ads linkage | GA4 property linked to Ads accounts `3820636025` and `4159217891`; imported GA4 actions exist but are secondary and zero-volume in checked evidence. |

USA remaining platform gaps:

| Area | Gap |
|---|---|
| Google Ads | USA account owner must confirm the correct Google Ads account and conversion action before any final USA helper-event conversion is used for bidding. |
| Meta | USA dataset/pixel ownership must be confirmed before Meta final helper-event tags are activated. |
| GA4 currency | USA property currency is currently CAD; confirm whether this should remain. |
| Processed reporting QA | Website source and GTM runtime are live, but processed GA4 reporting still needs delayed recheck. |

## Attribution Taxonomy

### Parent Form 4 Attribution Fields

| Payload field | Gravity Forms field | Meaning |
|---|---:|---|
| `utm_source` | `35` | Last/current UTM source |
| `utm_medium` | `36` | Last/current UTM medium |
| `utm_campaign` | `37` | Last/current UTM campaign |
| `utm_term` | `38` | UTM term |
| `utm_content` | `39` | UTM content |
| `gclid` | `40` | Google Ads click ID |
| `gbraid` | `41` | Google app/web privacy click ID |
| `wbraid` | `42` | Google web-to-app/privacy click ID |
| `fbclid` | `43` | Meta click ID |
| `msclkid` | `44` | Microsoft Ads click ID |
| `first_landing_page` | `45` | First known landing page |
| `first_referrer` | `46` | First known referrer |

### Franchise GAConnector Fields

| Payload field | Gravity Forms field | Meaning |
|---|---:|---|
| `lc_source` | `14` | Last-click source |
| `lc_medium` | `15` | Last-click medium |
| `lc_campaign` | `16` | Last-click campaign |
| `lc_content` | `17` | Last-click content |
| `lc_term` | `18` | Last-click term |
| `lc_channel` | `19` | Last-click channel |
| `lc_landing` | `20` | Last-click landing |
| `lc_referrer` | `21` | Last-click referrer |
| `fc_source` | `22` | First-click source |
| `fc_medium` | `23` | First-click medium |
| `fc_campaign` | `24` | First-click campaign |
| `fc_content` | `25` | First-click content |
| `fc_term` | `26` | First-click term |
| `fc_channel` | `27` | First-click channel |
| `fc_referrer` | `28` | First-click referrer |
| `gclid` | `29` | Google Ads click ID |
| `ga_client_id` | `30` | GA client ID |

## Naming Convention And UTM Rules

### Parent Local Listing UTMs

Governed source: `docs/40-naming-convention/local-listing-utm-rules-gbp-yelp-2026-05-03.md`

Upstream context source: `/Users/matthewbison/Desktop/cefa-nexus/CEFA/.agency/context/cefa-parents-local-listing-utm-rules-2026-05-03.md`

Scope:

- These rules cover CEFA parent-school location links from Google Business Profile and Yelp.
- They are separate from Meta ad naming conventions.
- Do not use Meta campaign tokens such as `LSM`, `FRANCH`, `META`, `TOF`, `BOF`, `IMG`, `VID`, or `CAR` in GBP/Yelp UTMs.

Canonical tokens:

| Token | Value |
|---|---|
| `utm_medium` | `local_listing` |
| GBP source | `google_business_profile` |
| Yelp source | `yelp` |
| GBP short token | `gbp` |
| Yelp short token | `yelp` |
| Location campaign | `parents_school_location` |
| Inquiry campaign | `parents_school_inquiry` |
| Naming version | `ll1` |
| School variable | `{school_slug}` using the canonical CEFA school page slug |

Website link rule:

```text
utm_source={platform}
utm_medium=local_listing
utm_campaign=parents_school_location
utm_content={school_slug}__website
utm_id=ll1__{platform_short}__{school_slug}
```

GBP website link:

```text
https://cefa.ca/cefa-find-a-school/{school_slug}/?utm_source=google_business_profile&utm_medium=local_listing&utm_campaign=parents_school_location&utm_content={school_slug}__website&utm_id=ll1__gbp__{school_slug}
```

Yelp website link:

```text
https://cefa.ca/cefa-find-a-school/{school_slug}/?utm_source=yelp&utm_medium=local_listing&utm_campaign=parents_school_location&utm_content={school_slug}__website&utm_id=ll1__yelp__{school_slug}
```

Inquiry form link rule:

```text
utm_source={platform}
utm_medium=local_listing
utm_campaign=parents_school_inquiry
utm_content={school_slug}__inquiry_form
utm_id=ll1__{platform_short}__{school_slug}__inquiry
```

GBP inquiry form link:

```text
https://cefa.ca/cefa-find-a-school/{school_slug}/?utm_source=google_business_profile&utm_medium=local_listing&utm_campaign=parents_school_inquiry&utm_content={school_slug}__inquiry_form&utm_id=ll1__gbp__{school_slug}__inquiry
```

Yelp inquiry form link:

```text
https://cefa.ca/cefa-find-a-school/{school_slug}/?utm_source=yelp&utm_medium=local_listing&utm_campaign=parents_school_inquiry&utm_content={school_slug}__inquiry_form&utm_id=ll1__yelp__{school_slug}__inquiry
```

Optional internal form label:

```text
parent_inquiry__{school_slug}__{platform_short}
```

Examples:

```text
parent_inquiry__burlington-south-service-road__gbp
parent_inquiry__burlington-south-service-road__yelp
```

Rules:

- Use lowercase values.
- Use hyphens inside `{school_slug}`.
- Use double underscores only to separate internal UTM components inside `utm_content` and `utm_id`.
- Keep `utm_campaign` stable across all schools so reporting can group all school-location traffic or all school-inquiry traffic.
- Put the school-specific value in `utm_content` and `utm_id`, not in `utm_campaign`.
- Do not use paid-media funnel, audience, format, or platform tokens from the Meta naming convention.
- Do not change `ll1` unless the local-listing UTM schema changes. If it changes, propose `ll2`.

Reporting interpretation:

| UTM field/value | Meaning |
|---|---|
| `utm_source=google_business_profile` | GBP listing traffic. |
| `utm_source=yelp` | Yelp listing traffic. |
| `utm_medium=local_listing` | Unpaid/local-directory listing traffic. |
| `utm_campaign=parents_school_location` | User clicked a general school-location link. |
| `utm_campaign=parents_school_inquiry` | Link was intended to drive a parent inquiry form. |
| `utm_content` | Identifies the school and link type. |
| `utm_id` | Stable machine key for joining across GA4, Looker Studio, Sheets, BigQuery, or CRM exports. |

## Metric Definitions

### Core Parent Enrollment Metrics

| Metric | Definition | Primary source | Status | Notes |
|---|---|---|---|---|
| Gravity Forms total leads | Count of saved valid parent Form 4 entries in the requested date range. | Gravity Forms Form 4 / local reconciliation | Partial/verified depending on access | This is the clean submission-count view, but not necessarily deduped like CRM. |
| Helper-plugin leads | GA4 `generate_lead` where `tracking_source=helper_plugin`, `form_id=4`, `form_family=parent_inquiry`, `inquiry_success=true`. | GA4 BigQuery export | Verified | Used to validate tracking path, not necessarily the authoritative business lead count. |
| Canonical CRM lead | GreenRope opportunity created in range, across lead-volume phases, deduped by school + month + child/program best-key. | GreenRope opportunities via Agentic Brain reconciliation | Verified current dashboard contract | Metric name: `crm_total_leads_child_dedup`. |
| Executive comparable leads | Canonical CRM reconciliation total when available; Gravity fallback only if CRM unavailable. | V2 executive / analytics API | Verified current product contract | Exposed as `total_leads_comparable`. |
| Paid lead, Gravity signal | Gravity/Form attribution has paid click ID or paid UTM/source-medium signal. | Gravity Forms fields / reconciliation | Partial | Exposed as `paid_inquiries_gravity` or `gravity_paid_inquiries_params`. Good comparator, but source labels must remain visible. |
| GreenRope ad-attributed inquiry signal | Inquiry-phase CRM opportunity has at least one recognized UTM/click-id field populated. | GreenRope `GetOpportunitiesRequest` aggregate in BigQuery | Partial | Dashboard field: `greenrope_ad_attributed_inquiries`. This is ad-attribution evidence only, not solid paid-media inquiry truth. |
| Paid lead, platform signal | Paid platform conversions from Meta + Google campaign data. | Ads/Supermetrics/BigQuery/ads routes | Partial | Exposed as `ads_paid_inquiries_total`, `paid_inquiries_meta`, `paid_inquiries_google`. Platform semantics differ from Gravity/CRM. |
| Tour | Phase-scoped opportunity count in CRM for tour phases. | GreenRope opportunities | Verified current product contract | Not deduped using the lead best-key. BI tour totals may differ. |
| Enrollment | Phase-scoped opportunity count where phase includes enrollment and closed won/won. | GreenRope opportunities | Verified current product contract | BI/reporting enrollments are reference/comparison, not automatically equivalent. |
| Application | A submitted application or application-stage opportunity, if CEFA formalizes this stage. | Not locked | Missing/needed | Current available docs do not define a governed application metric. |
| Lost lead | Opportunity/contact moved into a lost/disqualified/lost-review state or counted by lost-lead workflow activity. | GreenRope phases/activities | Partial | Operational `Lost Lead Review` activity exists as workflow signal; KPI definition still needs business signoff. |
| Lead-to-tour rate | `tours / leads`. | Derived | Partial | Must state source of numerator and denominator. |
| Tour-to-enroll rate | `enrollments / tours`. | Derived | Partial | Must state source of numerator and denominator. |
| Enrollment rate | Usually `enrollments / leads` or reporting-specific enrollment percent. | Derived / BI | Partial | Needs business definition lock when used in executive reporting. |
| Waitlisted | Count/status from BI/reporting or School Manager/CRM availability context. | BI/reporting reference today | Partial | Not yet locked as canonical metric. |
| Current school availability state | School + Program availability label/status. | WordPress School Manager today | Partial | GreenRope journey codes can support but are not authoritative by themselves. |

### GreenRope Dashboard Metrics

Current governed endpoint map: `docs/20-bigquery/greenrope-metric-definitions-and-api-map-2026-05-03.md`

| Dashboard metric | Endpoint | Source fields | Status | Interpretation |
|---|---|---|---|---|
| `greenrope_inquiries_total` | `GetOpportunitiesRequest` by `group_id` | Opportunity `phase` / `stage` / `status` | Partial | Count of opportunity rows in inquiry-like phases. It is CRM opportunity-state evidence, not final conversion truth. |
| `greenrope_ad_attributed_inquiries` | `GetOpportunitiesRequest` by `group_id` | Opportunity custom fields normalized to `utmsource`, `utmmedium`, `utmcampaign`, `gclid`, `gbraid`, `wbraid`, `fbclid`, or `msclkid` | Partial | Count of inquiry rows with UTM/click-id evidence. Do not label as GreenRope paid inquiries. |
| `greenrope_no_detected_ad_attribution_inquiries` | `GetOpportunitiesRequest` by `group_id` | Same custom-field set as above | Partial | Count of inquiry rows without detected UTM/click-id evidence. This does not prove organic source. |
| `greenrope_tour_phase_count` | `GetOpportunitiesRequest` by `group_id` | Opportunity `phase` / `stage` / `status` | Partial | Current phase evidence for tour-like phases, not an attended-tour ledger. |
| `greenrope_enrollment_phase_count` | `GetOpportunitiesRequest` by `group_id` | Opportunity `phase` / `stage` / `status` | Partial | Current phase evidence for won/enrollment-like phases, not the final operational enrollment ledger. |
| `raw_opportunity_count` | `GetOpportunitiesRequest` by `group_id` | Opportunity rows returned with usable date | Verified extraction count | Row count used for the daily aggregate. Not deduped lead truth. |
| `greenrope_group_id` / `greenrope_group_name` | `GetGroupsRequest`; `GetOpportunitiesRequest` request parameter | GreenRope group ID/name | Verified/partial | Mapping and QA fields. Not canonical CEFA school identity by themselves. |

Loaded support endpoints are currently limited to `GetGroupsRequest` and `GetOpportunitiesRequest`. `GetOpportunityFieldsRequest`, `GetPhasesRequest`, and `GetPhasePathsRequest` remain pending inputs for a more auditable field and phase dictionary.

### Date Window Definitions

| Term | Working definition | Status |
|---|---|---|
| MTD | Month-to-date from first day of current month through the selected/as-of date. | Needs final timezone signoff |
| YTD | Year-to-date from January 1 through the selected/as-of date. | Needs final timezone signoff |
| Exact month | Calendar month selected in reporting, usually month start to month end. | Verified product concept |
| Rolling 7/30 days | Relative date range ending today/as-of date. | Reference |
| Business timezone | Most current reporting code uses `America/Vancouver` in key marketing report paths, but some code may still use UTC day bounds. | Partial |

Recommendation: lock all stakeholder MTD/YTD reporting to a named timezone, preferably `America/Vancouver` unless school-local reporting is intentionally required.

### Paid Media And Efficiency Metrics

| Metric | Definition | Status |
|---|---|---|
| Spend | Ad spend from platform/reporting source for selected range. | Partial/available |
| Platform paid inquiries total | Meta paid inquiries + Google paid inquiries where platform data is available. | Partial/available |
| CPL / CPI | `spend / platform paid inquiries`; do not use GreenRope ad-attributed inquiry counts as the denominator unless the dashboard explicitly labels that comparator. | Derived; source-sensitive |
| CPC | `spend / clicks`. | Derived from ads platform data |
| CTR | `clicks / impressions`. | Derived from ads platform data |
| Session conversion rate | GA4 conversions or lead events divided by sessions. | Partial; must state event basis |
| ROAS | Not a parent enrollment primary metric unless revenue/enrollment value model is defined. | Future |

### Workflow And Engagement Metrics

| Metric | Definition | Source | Status |
|---|---|---|---|
| Tour Scheduled | CRM activity/workflow signal for scheduled tour activity. | GreenRope activities | Verified explanatory |
| Post Tour Follow-up | CRM activity signal for follow-up after tour. | GreenRope activities | Verified explanatory |
| Lost Lead Review | CRM activity signal for lost-lead review. | GreenRope activities | Verified explanatory |
| Event Tour Count | CRM event/appointment evidence. | GreenRope events | Partial/explanatory |
| Email engagement | Sent/read/click evidence. | GreenRope email activity | Partial/explanatory |
| Journey progress | Per-contact journey evidence. | GreenRope journeys | Partial/explanatory |

Workflow metrics explain operations. They should not silently replace canonical reporting leads, tours, or enrollments.

### Parent Insights Metrics

| Metric | Definition | Source | Status |
|---|---|---|---|
| Total sessions | Parent insight/chat sessions in selected range. | Parent Insights API | Separate domain |
| Analyzed sessions | Sessions with completed analysis. | Parent Insights API | Separate domain |
| Avg positivity | Sentiment/positivity score, usually 0-10 transformed from analysis/reviews. | Parent Insights / GBP fallback | Separate domain |
| Ready to tour percent | Share of analyzed sessions categorized as ready-to-tour. | Parent Insights analysis | Separate domain |
| Knowledge gap sessions | Sessions with knowledge-gap categories. | Parent Insights analysis | Separate domain |
| Failed analyses | Analysis failures by status. | Parent Insights API | Separate domain |

These metrics are not enrollment funnel truth. They are parent experience and content/answer-quality signals.

## Source Ownership By Dashboard Layer

| Layer | Purpose | Examples | Authority level |
|---|---|---|---|
| Canonical / reconciled | Defensible KPI truth. | CRM deduped leads, CRM tours/enrollments, Gravity paid comparator, paid-performance context. | Highest for V2 KPI surfaces. |
| BI / reporting | Month-end reporting context and operations comparisons. | BI monthly history, waitlisted, occupancy-style enrollment %, school ops snapshots. | Reference/comparison unless promoted. |
| Workflow / engagement | Explain why funnel numbers moved. | Activities, journey progress, email, follow-up, lost-lead review. | Explanatory, not KPI truth. |
| Separate domains | Useful but not funnel truth. | GA4 traffic, GBP reviews, Parent Insights, Budget Pacing. | Domain-specific. |
| Mixed operational | Control-room or mission-control telemetry. | Agent status, health monitors, operational alerts. | Not KPI truth. |

## Data Quality And Validation Rules

| Area | Rule |
|---|---|
| Event duplication | One successful parent Form 4 submission = one `school_inquiry_submit` = one browser `generate_lead`. |
| Event ID parity | Browser `event_id` must equal Gravity Forms `32.4` for parent Form 4. |
| Direct thank-you | Direct thank-you visits must not fire final conversions. |
| Reloads | Thank-you reloads must not fire duplicate final conversions. |
| Failed validation | Failed validation must fire no primary final conversion. |
| Field separation | Never emit collapsed Field 32 values as final payload parameters. |
| Add-on boundary | Gravity Forms GA add-on is not source of truth unless clean separated values and no duplicate risk are proven. |
| Server-side boundary | Measurement Protocol audit events must not be GA4 key events or imported to Ads. |
| Parent/franchise containment | Hostname/context filters must separate `cefa.ca`, `franchise.cefa.ca`, and `franchisecefa.com`. |
| Ad platform changes | Do not change Ads primary/secondary or Meta optimization settings from repo evidence alone; require platform-owner confirmation. |

## Privacy, PII, And Retention Rules

### Do Not Send To GA4, GTM, Ads, Meta, Or Public DataLayer

| Category | Examples |
|---|---|
| Parent PII | Parent/guardian name, email, phone, free-text notes. |
| Child PII | Child name, child DOB, child-specific notes. |
| Franchise contact PII | First name, last name, phone, email, full street address, company contact details. |
| High-cardinality/debug values | Full URLs when not necessary, raw referrers, click IDs as registered custom dimensions, GA client ID as custom dimension, Gravity Forms entry ID. |

Notes:

- Some click IDs and landing/referrer fields are stored in Gravity Forms or server-side records for attribution/reconciliation. That is different from registering them as GA4 custom dimensions or pushing them broadly into public destinations.
- Current GA4 custom dimensions intentionally exclude high-cardinality values such as `event_id`, click IDs, full URLs, landing URLs, referrers, GA client IDs, and Gravity Forms entry IDs.

### Retention Guidance For A Clean Data Project

| Data class | Recommendation |
|---|---|
| Raw Gravity Forms entries | Keep raw immutable pulls, but restrict PII access and define retention. |
| Raw GreenRope payloads | Keep raw pulls for audit/reconciliation, with PII access controls. |
| Clean facts and dimensions | Keep long-term for reporting, with PII minimized. |
| Tracking/debug logs | Short retention unless needed for audit. |
| AI runtime/checkpoint logs | Do not store unlimited runtime/checkpoint tables in the foundational database. |
| Parent Insights transcripts | Redact or minimize content by default; keep analytic outputs separate from raw sensitive content. |

## Recommended Clean Data Model

### Dimensions

| Table | Grain | Purpose |
|---|---|---|
| `dim_school` | One row per `school_uuid` | Stable school/location identity across WordPress, GreenRope, Gravity, GA4, GBP, PiinPoint, ads. |
| `dim_program` | One row per `program_id` | Baby, JK1, JK2, JK3, Weekend Care, Waitlist/status. |
| `dim_source` | One row per source/platform/channel | Normalize source families and source ownership. |
| `dim_campaign` | One row per platform campaign/ad naming unit | Paid-media mapping to school/program where possible. |
| `dim_metric` or `metric_definitions` | One row per governed metric | Lock formula, owner, date grain, source priority, and business meaning. |

### Raw Tables

| Table | Purpose |
|---|---|
| `raw_gravity_forms_entries` | Untouched parent/franchise form entries and metadata. |
| `raw_greenrope_groups` | CRM group/location context. |
| `raw_greenrope_contacts` | CRM contact records, access-restricted. |
| `raw_greenrope_opportunities` | CRM funnel objects. |
| `raw_greenrope_activities` | CRM workflow/activity evidence. |
| `raw_greenrope_events` | CRM appointments/events. |
| `raw_ga4_events` | GA4 export or selected event pull. |
| `raw_marketing_spend` | Google/Meta/Supermetrics spend and conversion records. |
| `raw_gbp_locations` | GBP location export. |
| `raw_gbp_reviews` | GBP reviews/sentiment context, access-aware. |
| `raw_school_manager_availability` | School Manager availability snapshots. |

### Normalized Facts

| Table | Grain | Purpose |
|---|---|---|
| `fact_leads` | One normalized lead/inquiry signal | Canonical lead reporting and source reconciliation. |
| `fact_paid_signals` | One paid attribution/conversion signal | Paid-source signal audit across Gravity, CRM, platform. |
| `fact_tours` | One tour/reporting signal | CRM and BI tour reconciliation. |
| `fact_applications` | One application signal | Future if application stage becomes defined. |
| `fact_enrollments` | One enrollment signal | CRM/BI enrollment reconciliation. |
| `fact_marketing_spend` | Date + platform + campaign + school/program where known | Spend, CPL, pacing. |
| `fact_school_availability_snapshot` | School + program + effective date | Availability/state history from School Manager and future CRM/KinderTales bridge. |
| `fact_parent_insight_sessions` | Session/date/school where matched | Parent chatbot/sentiment/readiness insights. |

### Serving Marts

| Mart / view | Purpose |
|---|---|
| `mart_school_monthly` | School-level monthly KPI reporting. |
| `mart_school_program_monthly` | School + program monthly reporting. |
| `mart_executive_monthly` | Network-level executive metrics. |
| `mart_source_coverage` | Freshness, row counts, missing mappings, source health. |
| `mart_school_current_state` | Current availability, operational status, and latest KPI context by school. |

## Required Freshness And Audit Tables

| Table | Required fields |
|---|---|
| `sync_runs` | source, started_at, finished_at, status, row_count, error_message, source_cursor/checkpoint. |
| `mapping_review_queue` | field, source_value, proposed_match, confidence, status, reviewer, reviewed_at. |
| `data_quality_checks` | check_name, source, period, expected, actual, status, details. |
| `source_coverage_daily` | source, date, schools_mapped, schools_missing, rows_loaded, latest_source_timestamp. |

## Availability And School Current State

Current best-practice hierarchy:

| Layer | Role |
|---|---|
| WordPress School Manager | Operational write/read surface for school/program availability today. |
| GreenRope / CRM+ | Lead, opportunity, journey, workflow, and support context. Not the live availability matrix by itself. |
| KinderTales / enrollment automation | Future automation candidate if school + program capacity/enrollment is structured and reliable. |
| Spreadsheet bridge | Practical interim control layer at School + Program grain before full automation. |

Recommended availability bridge grain:

| Field | Meaning |
|---|---|
| `school_uuid` | Stable school key. |
| `wordpress_school_manager_id` | WordPress/School Manager write target. |
| `greenrope_group_id` | CRM school/group context. |
| `program_id` | Program key. |
| `program_key` | Normalized program alias. |
| `availability_label` | Parent-facing label, e.g. Space available, School full, Weekend Program. |
| `kt_journey_code` | KinderTales/CRM journey code when confirmed. |
| `effective_date` | Start date of availability state. |
| `last_verified_by` | Human/system verifier. |
| `last_verified_at` | Verification timestamp. |
| `notes` | Controlled notes, not free-form PII. |

Known availability/journey code labels observed earlier:

| KT code | Label |
|---:|---|
| 1 | Space available |
| 2 | School full (recommend nearby) |
| 3 | Future school |
| 4 | School nearby schools full |
| 5 | Space available (tuition sheet) |
| 7 | Weekend Program |
| 8 | School full (recommend Weekend Program) |
| 9 | Space available (Calgary - with tuition) |
| 10 | Space available (Carly schools) |

These labels still need a governed mapping to School Manager availability fields, CRM/KinderTales journey codes, and reporting statuses.

## Current Known Gaps And Decisions Needed

### Critical Identity Gaps

| Gap | Decision / action needed |
|---|---|
| 2 WordPress School Manager IDs missing | Confirm South Surrey - Morgan Crossing East and Surrey - Panorama North. |
| 4 Gravity routing gaps | Confirm South Surrey - Morgan Crossing East, Surrey - Cloverdale, Surrey - Panorama North, Surrey - Sullivan Ridge. |
| 6 GBP gaps | Confirm Calgary - Northland, Langley - Willowbrook, Richmond - Crestwood, Surrey - Panorama North, Vancouver - Kitsilano, Victoria - Douglas. |
| 13 mixed-format `canonical_location_id` rows | Normalize to one format or explicitly approve slug-key rows. |
| PiinPoint bridge key missing | Populate deterministic keys or keep PiinPoint matching as non-authoritative fallback. |
| Ad naming token incomplete | Confirm whether 38 schools are missing mappings or simply have no active paid campaigns. |
| KinderTales ID equivalence | Confirm whether `school_uuid` is truly the KinderTales ID everywhere. |
| Duplicate GreenRope group `50` | Decide whether South Surrey - Morgan Crossing and South Surrey - Morgan Crossing East need separate CRM groups, a split rule, or a manual review process. |

### Metric Governance Gaps

| Metric / area | Needed decision |
|---|---|
| Total lead | Decide when stakeholder reporting should use Gravity total submissions vs CRM deduped leads. |
| Paid/ad-attributed lead | Keep Gravity paid params, GreenRope ad-attributed inquiry evidence, and platform conversions as separately labeled metrics until a reconciled paid-lead definition is approved. |
| Tour | Lock BI/reporting tour definition vs CRM phase-scoped tour count. |
| Enrollment | Lock BI/reporting enrollment definition vs CRM won/enrollment phase count. |
| Waitlist | Decide if it is program, status, or both. |
| Current school availability | Define final school + program availability states and owner. |
| MTD/YTD | Lock timezone and inclusive/exclusive date boundaries. |
| Franchise conversions | Confirm Canada/USA Ads primary-secondary and Meta custom conversion/dataset decisions. |

### Platform Gaps

| Platform | Gap |
|---|---|
| Google Ads parent | Confirm conversion action primary/secondary status in Ads UI/API before bidding signoff. |
| Meta parent | Confirm Events Manager custom conversion / optimization status. |
| Franchise Canada Meta | Custom conversion status inside current shared dataset still needs Events Manager verification. |
| Franchise USA Ads | Confirm USA-specific conversion labels before activating Ads final helper tags. |
| Franchise USA Meta | Confirm USA dataset/pixel before activating Meta final helper tags. |
| Parent business-truth marts | Refresh parent inquiry marts beyond 2026-03-29 before current MTD/YTD business reporting. |
| Franchise business-truth marts | Refresh franchise lead-source mart beyond 2026-03-29 before current franchise reporting. |
| Google/Supermetrics freshness | Explain or refresh checked detail after 2026-04-30 before current paid-media claims. |
| Meta May paid zeros | Resolve why native Meta rows exist through 2026-05-02 while May 1/2 dashboard paid metrics are zero. |
| GA4 Data API runtime access | Decide whether service-account/runtime GA4 Data API access is needed, or continue to use native GA4 BigQuery export as the reporting path. |
| GreenRope refresh automation | Add a scheduled refresh before dashboards depend on the GreenRope aggregate daily. |
| GreenRope field dictionary | Load or snapshot `GetOpportunityFieldsRequest` before treating custom-field matching as fully governed. |
| GreenRope phase taxonomy | Load or snapshot `GetPhasesRequest` and `GetPhasePathsRequest` before treating phase matching as fully governed. |
| Rule registry upload workflow | Create a controlled upload process for future conversion-tracking and naming-convention rule changes. |
| Server-side tracking | Keep MP audit-only until browser/GTM parity is stable and dedupe design is explicit. |

## Future Conversion Tracking Roadmap

This is the consolidated forward plan for the conversion-tracking repo. It extends the existing franchise roadmap and CAPI/sGTM roadmap into one source-governed sequence.

### Phase 0: Governance And Taxonomy Lock

Goal: make the current data foundation safe before adding more tracking layers.

| Work item | Output | Status |
|---|---|---|
| Lock `dim_school` primary key | `school_uuid` accepted as parent conversion join key. | Started / current rule |
| Lock `dim_program` primary key | `program_id` accepted as program join key. | Started / observed values known |
| Resolve school identity gaps | WordPress IDs, Gravity routing, GBP IDs, PiinPoint key, ad tokens. | Open |
| Lock metric definitions | Total lead, paid/ad-attributed lead, tour, application, enrollment, lost lead, MTD/YTD. | Open |
| Lock date boundary | Named timezone and inclusive/exclusive rules for MTD/YTD/monthly reporting. | Open |
| Lock PII rules | Approved fields for dataLayer, GA4, Ads, Meta, raw storage, and reporting marts. | Started |

Acceptance gate:

```text
Every dashboard metric has an owner, formula, source priority, date boundary, and PII rule.
```

### Phase 1: Browser-Side Conversion Stability

Goal: keep the current confirmed-success browser path clean and trusted.

| Surface | Required final state | Status |
|---|---|---|
| Parent `cefa.ca` | One successful Form 4 submission creates one `school_inquiry_submit`, then GTM maps to GA4 `generate_lead`, Ads, and Meta. | Mostly verified |
| Franchise Canada | Form 1 creates one `franchise_inquiry_submit`; Form 2 creates one `real_estate_site_submit`; hostname and context contained. | Verified with some platform confirmations still open |
| Franchise USA | Form 1/Form 2 helper events mapped to USA GA4; Ads/Meta final tags wait for USA-specific labels/dataset. | In progress |
| Micro-events | Diagnostic only; not bidding conversions. | Started |
| Legacy cleanup | Old thank-you/pageview and Elementor/form-submit final tags paused or demoted only after replacement path is proven. | Partial |

Acceptance gate:

```text
One saved form submission = one final helper event = one intended platform lead event, with no direct-thank-you or reload false positives.
```

### Phase 2: Clean Reporting Data Layer

Goal: stop reporting directly from messy raw imports and build an auditable data layer.

| Work item | Output | Status |
|---|---|---|
| Raw layer | `raw_gravity_forms_entries`, `raw_greenrope_*`, `raw_ga4_events`, `raw_marketing_spend`, `raw_gbp_*`, `raw_school_manager_availability`. | Future; current GreenRope BigQuery load is aggregate counts only |
| Normalized facts | `fact_leads`, `fact_paid_signals`, `fact_tours`, `fact_applications`, `fact_enrollments`, `fact_marketing_spend`, `fact_school_availability_snapshot`. | Future |
| Marts | `mart_school_monthly`, `mart_school_program_monthly`, `mart_executive_monthly`, `mart_source_coverage`, `mart_school_current_state`. | Future |
| Freshness checks | `sync_runs`, row counts, latest timestamps, error logs, source coverage. | Future |
| Mapping QA | `mapping_review_queue` for unmatched school/program/source values. | Future |

Acceptance gate:

```text
Dashboards read from normalized marts/views, while raw source pulls remain separately auditable.
```

### Phase 3: Server-Side Audit Layer

Goal: add server-side confirmation without duplicating primary conversions.

| Work item | Output | Status |
|---|---|---|
| Parent server audit | `school_inquiry_submit_server_audit`, not GA4 `generate_lead`. | Future |
| Franchise server audit | `franchise_*_server_audit` events, not second primary `generate_lead`. | Future |
| Event parity | Browser event, server audit event, and saved Gravity Forms entry share the same `event_id`. | Future |
| Validation endpoint | If CEFA-owned MP sender is built, validate payloads before production collection. | Future |
| Audit-only reporting | Server audit events are not GA4 key events and not imported into Ads. | Future |

Acceptance gate:

```text
One valid form entry = one browser primary event = zero or one server audit event, both sharing the same event_id.
```

### Phase 4: CEFA Collector And CAPI

Goal: move from ad hoc server audit to CEFA-owned durable event collection and controlled platform dispatch.

| Work item | Output | Status |
|---|---|---|
| Collector endpoint | Signed Gravity Forms/helper payload intake. | Future |
| Durable event store | Validated event record before outbound dispatch. | Future |
| Meta CAPI | Browser/CAPI dedupe using same event name and same `event_id`. | Future |
| Google offline/enhanced conversions | Only after legal/PII and platform-owner approvals. | Future |
| LinkedIn / other lifecycle uploads | Add only after primary source and dedupe model are stable. | Future |
| Dataset separation | Parent, Franchise Canada, and Franchise USA dispatch to the correct dataset/pixel during transition. | Future |

Acceptance gate:

```text
The collector can prove what was received, what was rejected, what was dispatched, and what matched the browser event.
```

### Phase 5: sGTM And First-Party Routing

Goal: improve durability, governance, privacy controls, and BigQuery handoff after event contracts are stable.

Recommended future server domains:

| Surface | Possible server domain |
|---|---|
| Parent | `metrics.cefa.ca` or `collect.cefa.ca` |
| Franchise Canada | `metrics.franchise.cefa.ca` or `collect.franchise.cefa.ca` |
| Franchise USA | `metrics.franchisecefa.com` or `collect.franchisecefa.com` |

Phase 5 should not begin until:

- browser parity is proven
- source-of-truth tables exist
- event IDs are stable
- platform datasets/properties are confirmed
- consent, DNS, cookie-domain, and privacy implications are reviewed

Acceptance gate:

```text
sGTM improves routing and governance; it does not become a workaround for unclear source ownership.
```

### Phase 6: Availability And Lifecycle Automation

Goal: connect operational school/program state back to the website after the identity layer is trusted.

| Work item | Output | Status |
|---|---|---|
| Availability bridge | School + Program table with WP School Manager ID, GreenRope group ID, KinderTales ID, program ID, availability label, KT journey code, audit fields. | Started as design |
| School Manager writeback | Controlled update path into WordPress School Manager availability fields. | Future |
| CRM/KinderTales support | CRM journey codes support routing/status; enrollment automation comes later. | Future |
| Availability snapshots | Historical `fact_school_availability_snapshot`. | Future |
| Current-state mart | `mart_school_current_state` for dashboards and website state. | Future |

Acceptance gate:

```text
A reviewed school/program current-state record can update WordPress School Manager without manual duplicate entry or CRM label guessing.
```

### Future Plan Guardrails

| Guardrail | Rule |
|---|---|
| No duplicate conversions | Do not run browser `generate_lead` and server `generate_lead` for the same form at the same time. |
| No parent/franchise bleed | Parent enrollment, Franchise Canada, and Franchise USA remain separately scoped. |
| No PII in ad platforms | Do not push names, emails, phones, child DOB, notes, addresses, or free text to dataLayer/GA4/Ads/Meta. |
| No advanced layer before truth layer | CAPI, sGTM, and lifecycle uploads wait until event identity and source ownership are stable. |
| No label-only joins | Stable IDs beat labels, slugs, and campaign names. |
| No silent source swaps | Any metric source change must update metric definitions and source ownership docs. |

## Immediate Build Priorities For A Clean Supabase / Data Foundation

1. Create `dim_school` using `school_uuid` as the primary key and load all known 53 rows from the current reference.
2. Create `dim_program` using the 6 observed program rows, with `waitlist` marked for business modeling review.
3. Create raw source tables separately from clean fact/mart tables.
4. Use `cefa_core.measurement_rule_registry` as the current seeded rule-reference surface, but create fuller `metric_definitions` before exposing new stakeholder KPI dashboards.
5. Add `sync_runs`, `mapping_review_queue`, and `source_coverage_daily` from day one.
6. Automate the current counts-only GreenRope aggregate only after the duplicate group `50`, field dictionary, and phase taxonomy gaps are handled or clearly labeled.
7. Ingest Gravity Forms and deeper GreenRope raw/stage tables first, because those define submissions and CRM funnel truth.
8. Add GA4/BigQuery and paid media after the school/program joins are stable.
9. Add GBP and Parent Insights as separate domains, not funnel truth.
10. Keep AI/runtime/checkpoint tables out of the foundational database.
11. Only push availability back to WordPress School Manager after a reviewed School + Program availability bridge exists.

## Maintenance Rule

When a missing external ID, metric definition, or platform decision is confirmed, update this document and the narrower source document in the same change when possible.

Do not promote a field from Partial or Missing to Verified based only on labels, slugs, campaign names, or one-off screenshots. Use a populated source table/export/API, live endpoint, or signed-off business definition.
