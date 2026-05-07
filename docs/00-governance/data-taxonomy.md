# CEFA Data Taxonomy And Source Map

Last updated: 2026-05-07

## Purpose

This file is the repo-level map for CEFA marketing measurement data. It connects the major data sources, stable identifiers, naming-convention keys, conversion-tracking events, warehouse surfaces, and owning workstream docs.

It is an index and routing file, not a replacement for the narrower source-of-truth documents. If a fact changes, update the narrow owning workstream first, then update this map if the source relationship or taxonomy changes.

## Status

`Partial`

- `Verified`: The source groups, key names, workstream owners, and links below are derived from the governed repo docs and runtime plugin README.
- `Partial`: Some source freshness, platform reporting, CRM mappings, school/location reconciliation, and paid-media inventories are only verified as of the dates in their owning docs.
- `Pending`: This file has not been backed by a machine-readable `data/reference/` taxonomy table yet.
- `Open question`: Whether this should become a dashboard-readable rule/source registry upload alongside `cefa_core.measurement_rule_registry`.

## How To Use This File

Use this file when deciding:

- which source answers a data question;
- which identifier should be used for joins;
- which name is only a display label;
- where a naming or conversion tracking change belongs;
- whether a metric is business truth, platform reporting, or diagnostic only.

Do not use this file to approve live changes. Live GTM, GA4, Google Ads, Meta, WordPress, BigQuery, budget, or CRM writes still require explicit user approval and the owning workstream's guardrails.

## Authority Order

Use the existing repo authority order from [source-of-truth-rules.md](./source-of-truth-rules.md):

1. Live verified systems and current API/browser/network evidence.
2. Runtime code and current governed repo docs.
3. Local CEFA conversion-tracking knowledge base for unmigrated evidence.
4. Local NEXUS context.
5. Explicitly cited CEFA Ops/source files.
6. External best practices.

## Primary Data Source Taxonomy

| Source group | System / source | Owns | Stable IDs / join keys | Naming / label fields | Conversion-tracking role | Reporting / warehouse landing | Status | Owning docs |
|---|---|---|---|---|---|---|---|---|
| Website runtime | Parent `cefa.ca` WordPress | Parent inquiry pages, Form 4 runtime, helper plugin output, School Manager context | Form 4 entry ID, `event_id`, `school_selected_id`, `program_id` | page path, school slug, school name, program name | Emits neutral parent event through helper plugin after saved submission | GA4 export, BigQuery marts, dashboard views | `Verified` for current contract | [README](../../README.md), [conversion tracking README](../10-conversion-tracking/README.md) |
| Website runtime | Franchise Canada `franchise.cefa.ca` | Canada franchise inquiry and real-estate/site forms | Gravity Forms entry ID, entry-meta `event_id`, Synuma lead ID when returned | market, location interest, form family | Emits `franchise_inquiry_submit` and `real_estate_site_submit` through WPCode/helper path | GA4, Google Ads, Meta, future warehouse reconciliation | `Partial` pending delayed platform confirmations | [event ownership matrix](../10-conversion-tracking/event-ownership-matrix-2026-05-05.md) |
| Website runtime | Franchise USA `www.franchisecefa.com` | USA franchise inquiry and real-estate/site forms | Gravity Forms entry ID, entry-meta `event_id`, Synuma lead ID when returned | market, location interest, form family | Emits USA franchise helper events; Google Ads final mapping still pending | GA4, Meta USA dataset, future warehouse reconciliation | `Partial` | [event ownership matrix](../10-conversion-tracking/event-ownership-matrix-2026-05-05.md) |
| Form/business truth | Gravity Forms parent Form 4 | Saved parent inquiry record | Form 4 entry ID, `32.1` school UUID, `32.2` program ID, `32.4` event ID | `32.5` school slug, `32.6` school name, `32.7` program name | Business truth behind parent final event | Parent inquiry marts after refresh; current marts are stale | `Verified` contract; `Partial` current reporting freshness | [business truth gaps](../10-conversion-tracking/business-truth-and-tracking-data-gaps-2026-05-03.md) |
| Form/business truth | Franchise Gravity Forms 1 and 2 | Franchise inquiry and site inquiry saved records | Form entry ID, helper entry-meta `event_id`, CRM lead ID when available | form family, lead intent, market/country | Business truth behind franchise helper events | Franchise lead-source mart after refresh; current mart is stale | `Partial` | [event ownership matrix](../10-conversion-tracking/event-ownership-matrix-2026-05-05.md) |
| Website metadata | CEFA School Manager | Parent school/program/day rendering and Field 32 behavior | `school_uuid`, `program_id`, School Manager IDs where known | school/program/day labels, school slug | Provides parent selected school/program context; helper plugin must not overwrite business fields | Master-data crosswalk and dim school reconciliation | `Verified` operational surface; some IDs `Partial` | [master data README](../60-master-data/README.md) |
| Tracking bridge | CEFA Conversion Tracking plugin | Neutral browser events, event ID lifecycle, duplicate guards, attribution backfill | `event_id`, one-time token, Form 4 field 32.4, franchise entry meta | `tracking_source=helper_plugin`, form family, lead intent | Website-side controlled event source | GA4/GTM/platform destinations; BigQuery GA4 export | `Verified` for documented contract | [README](../../README.md), [DataLayer contract](../phase1a/datalayer-contract.md) |
| Tracking bridge | Franchise WPCode fallback | Temporary bridge for live franchise hosts | entry-meta `event_id`; form IDs 1 and 2 | `site_context`, `market`, `country` | Emits franchise final events where full plugin deploy is blocked | GTM containers and downstream platforms | `Partial` | [conversion tracking README](../10-conversion-tracking/README.md) |
| Attribution capture | Parent first-party attribution fields | UTM/click/referrer handoff for parent Form 4 | Form 4 fields 35-46 | `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`, `gclid`, `gbraid`, `wbraid`, `fbclid`, `msclkid`, first landing/referrer | Attribution metadata, not lead truth by itself | GA4, BigQuery, future offline exports | `Verified` field contract | [README](../../README.md) |
| Attribution capture | GAConnector franchise fields | Franchise last-click/first-click attribution fields | Franchise fields 14-30 | `lc_*`, `fc_*`, `gclid`, `ga_client_id` | Preserve vendor attribution; helper should read, not overwrite | GA4/GTM/reporting when clean | `Partial` | [event ownership matrix](../10-conversion-tracking/event-ownership-matrix-2026-05-05.md) |
| Tag management | Parent GTM `GTM-NZ6N7WNC` | Maps parent neutral events to GA4, Google Ads, Meta | GTM tags/triggers; destination conversion labels | destination event names | Maps `school_inquiry_submit` to platform destinations | Platform reporting and GA4 export | `Verified` current parent path | [event ownership matrix](../10-conversion-tracking/event-ownership-matrix-2026-05-05.md) |
| Tag management | Franchise Canada GTM `GTM-TPJGHFS` | Maps Canada franchise events | GTM version/tag IDs; destination labels | destination event names | Preserves `fr_application_submit` / `Fr Application Submit` continuity | Platform reporting | `Partial` pending delayed confirmations | [event ownership matrix](../10-conversion-tracking/event-ownership-matrix-2026-05-05.md) |
| Tag management | Franchise USA GTM `GTM-5LZMHBZL` | Maps USA franchise events | GTM version/tag IDs; destination labels | destination event names | GA4/Meta active; Google Ads final-submit mapping pending | Platform reporting | `Partial` | [event ownership matrix](../10-conversion-tracking/event-ownership-matrix-2026-05-05.md) |
| Analytics | GA4 parent property `267558140` / `G-T65G018LYB` | Parent web event analytics | `event_id`, `event_name`, `user_pseudo_id`, session dimensions | GA4 event/parameter names | Receives mapped `generate_lead`; not CRM truth | `analytics_267558140.events_*`, GA4 marts | `Verified` export availability in checked docs | [warehouse current state](../20-bigquery/warehouse-current-state-2026-05-03.md) |
| Analytics | GA4 franchise Canada `259747921` / `G-6EMKPZD7RD` | Franchise Canada event analytics | GA4 event and parameter IDs | GA4 event names | Receives mapped `generate_lead`; not CRM truth | future/reported franchise surfaces | `Partial` | [event ownership matrix](../10-conversion-tracking/event-ownership-matrix-2026-05-05.md) |
| Analytics | GA4 franchise USA `519783092` / `G-YL1KQPWV0M` | Franchise USA event analytics | GA4 event and parameter IDs | GA4 event names | Receives helper-submit reporting; not CRM truth | future/reported franchise surfaces | `Partial` | [event ownership matrix](../10-conversion-tracking/event-ownership-matrix-2026-05-05.md) |
| Paid platform | Google Ads parent / `CEFA $3000` | Parent paid search/PMax execution and platform conversions | `customer_id`, `campaign_id`, `ad_group_id`, `asset_group_id`, `ad_id`, `gclid` | campaign/ad group/asset group labels; GADS1 keys | Destination conversion reporting; not business truth alone | `raw_google_ads`, Google Ads marts, Supermetrics detail | `Partial` freshness after 2026-04-30 | [Google Ads GADS1 inventory](../40-naming-convention/google-ads-naming-gads1-active-last-30-inventory-2026-05-04.md), [paid media availability](../50-paid-media/platform-data-availability-2026-05-03.md) |
| Paid platform | Google Ads franchise / `CEFA Franchisor` | Franchise paid search/PMax execution and platform conversions | `customer_id`, `campaign_id`, `ad_group_id`, `asset_group_id`, `ad_id`, `gclid` | campaign/ad group/asset group labels; GADS1 keys | Destination conversion reporting; USA final mapping still pending | `raw_google_ads`, Supermetrics detail | `Partial` | [Google Ads GADS1 inventory](../40-naming-convention/google-ads-naming-gads1-active-last-30-inventory-2026-05-04.md) |
| Paid platform | Meta parent / CEFA Early Learning | Parent Meta campaigns, ad sets, ads, pixel/dataset conversion reporting | `account_id`, `campaign_id`, `adset_id`, `ad_id`, `fbclid` | current names, NC1/NC2 names, campaign/ad/adset keys | Destination conversion reporting; not business truth alone | `raw_meta_ads`, Meta marts, Supermetrics detail | `Verified` inventory; `Partial` reporting freshness | [Meta NC2 inventory](../40-naming-convention/meta-naming-nc2-active-last-30-inventory-2026-05-04.md) |
| Paid platform | Meta franchise / CEFA Franchisor | Franchise Meta campaigns, ad sets, ads, shared/USA dataset paths | `account_id`, `campaign_id`, `adset_id`, `ad_id`, `fbclid` | current names, NC2 names, campaign/ad/adset keys | Destination conversion reporting; dataset strategy differs by market | `raw_meta_ads`, Meta marts, Supermetrics detail | `Partial` | [Meta NC2 inventory](../40-naming-convention/meta-naming-nc2-active-last-30-inventory-2026-05-04.md) |
| Naming/build control | v21 paid-media naming Google Sheet | Team-facing copy, creative, build manifest, paused import outputs | `campaign_slot`, `copy_template_slot`, `copy_render_slot`, `creative_slot`, build row ID | `campaign_key`, `ad_set_key`, `ad_data_key`, `ad_build_key`, creative filename | Controls future import-ready rows; does not approve live launch | Future n8n/import/audit outputs | `Partial` POC; verified sheet repair | [v21 build control doc](../40-naming-convention/paid-media-build-control-center-v21-final-poc-2026-05-06.md) |
| Naming/build control | Meta and Google active object inventory CSVs | ID-backed rename/build crosswalks | platform object IDs by level | current names, proposed NC2/GADS1 names, proposed keys | Required for safe rename/import and conversion joins | `data/reference/` CSVs | `Verified` as read inventory; proposed names `Partial` | [Meta NC2 inventory](../40-naming-convention/meta-naming-nc2-active-last-30-inventory-2026-05-04.md), [Google GADS1 inventory](../40-naming-convention/google-ads-naming-gads1-active-last-30-inventory-2026-05-04.md) |
| Budget planning | OneDrive/SharePoint `Budgets 25'26.xlsx` | Canonical monthly budget planning | budget row identity, budget group, location/group | budget scope, funding/source labels | Planning/reference only; not conversion truth | v21 sheet read-only budget mirror when synced | `Verified` source path; no live budget writes | CEFA repo `AGENTS.md`, [v21 build control doc](../40-naming-convention/paid-media-build-control-center-v21-final-poc-2026-05-06.md) |
| CRM/opportunity | GreenRope | Current-state opportunity aggregate and group mapping | GreenRope group ID, opportunity created date | opportunity phase/path labels; UTM/click markers | CRM context only; current aggregate is not final paid inquiry truth | `bridge_greenrope_group_school`, `fct_greenrope_school_funnel_daily`, dashboard CRM views | extraction count `Verified`; business interpretation `Partial` | [dashboard source layer](../20-bigquery/dashboard-source-layer-greenrope-and-rule-registry-2026-05-03.md) |
| CRM/franchise delivery | Synuma / SiteZeus / CEFA Franchise API | Franchise lead delivery and routing | `cefa_synuma_lead_id` where returned | routing owner/market fields | Franchise business delivery evidence | future franchise reconciliation | `Partial` | [event ownership matrix](../10-conversion-tracking/event-ownership-matrix-2026-05-05.md) |
| Business destination | KinderTales | Parent lead/delivery destination | current mapped lead/school identifiers when available | parent enrollment labels | Business destination; not replaced by plugin | future parent business-truth marts | `Pending` current refresh | [business truth gaps](../10-conversion-tracking/business-truth-and-tracking-data-gaps-2026-05-03.md) |
| Warehouse | BigQuery project `marketing-api-488017` | Raw, staging, mart, dashboard, rule-registry surfaces | table/view keys by source; `school_uuid`; platform IDs | mart field names, rule rows | Reconciles source evidence; does not replace form/CRM truth | `analytics_267558140`, `raw_*`, `mart_*`, `cefa_core` | `Verified` current state with gaps | [warehouse current state](../20-bigquery/warehouse-current-state-2026-05-03.md) |
| Reporting connector | Supermetrics | Paid platform and GA4 reporting extracts | account IDs, report dates, campaign/ad IDs where available | connector field labels | Reporting source, not live admin truth | `raw_supermetrics`, local artifacts | `Partial` | [paid media availability](../50-paid-media/platform-data-availability-2026-05-03.md) |
| Local SEO/listings | GBP and Yelp | Parent school local-listing traffic links | GBP/Yelp location IDs when mapped; `school_slug` in UTMs | `ll1` UTM fields | Source/medium attribution into GA4/BigQuery | GA4 and source/medium marts after tagging | `Partial` | [local listing UTM rules](../40-naming-convention/local-listing-utm-rules-gbp-yelp-2026-05-03.md) |
| Organic search | Google Search Console | Organic query/page performance | URL/page path, query, date | SEO page labels | SEO reporting only; not conversion truth | future SEO/GSC marts or reports | `Partial` snapshot | [SEO README](../30-seo/README.md) |
| SEO research | DataForSEO | Keyword/SERP and local SEO research | query/location/device fields | keyword and SERP labels | Research/reference only | SEO docs/artifacts | `Partial` | [SEO README](../30-seo/README.md) |
| Master reference | `mart_marketing.dim_school` | Current checked school dimension | `school_uuid`, `school_slug`, `canonical_location_id`, location fields | school display labels | Primary school join reference for parent tracking/reporting | dashboard and Looker marts/views | `Verified` 53-row coverage; some fields `Partial` | [school dimension coverage](../60-master-data/school-dimension-warehouse-coverage-2026-05-03.md) |
| Master reference | School form programs Google Sheet | Parent school URLs, inquiry URLs, shown programs | sheet school ID, school slug | school/program display labels | Input for location/form URL and program dropdown validation | naming sheet and master-data reconciliation | `Partial` 51 vs 53 school rows | [school form programs source](../60-master-data/school-form-programs-google-sheet-source-2026-05-04.md) |
| Dashboard rules | `cefa_core.measurement_rule_registry` and `vw_measurement_rule_registry_current` | Dashboard-readable rule references | `rule_family`, `rule_scope`, lifecycle/status fields | conversion/naming rule labels | Exposes current rules to dashboards; not source approval by itself | `mart_marketing.vw_measurement_rule_registry_current` | `Verified` seeded surface; upload workflow `Pending` | [dashboard source layer](../20-bigquery/dashboard-source-layer-greenrope-and-rule-registry-2026-05-03.md) |

## Canonical Identifier Taxonomy

| Identifier | Primary meaning | Use as join key? | Status | Do not confuse with |
|---|---|---:|---|---|
| `event_id` | Unique successful conversion-event identity | Yes, for event dedupe/reconciliation | `Verified` | `school_uuid`, `school_slug`, `campaign_id` |
| `school_uuid` | Parent school identity from Field 32 / `dim_school` | Yes, primary parent school join | `Verified` | display school name, location code |
| `school_selected_id` | Helper payload name for selected parent school UUID | Yes, maps to `school_uuid` | `Verified` | event ID |
| `program_id` | Selected parent program identity where available | Yes, for program-level parent tracking | `Verified` for observed programs | `program_token` |
| `program_label` | Human label for a parent program | No, label only | `Verified` in naming sheet | `program_token` |
| `program_token` | Naming/UTM-safe parent program token | Yes, for naming/reporting keys | `Verified` in v21 sheet | `program_id` |
| `franchise_topic` | Franchise ad/copy topic token | Yes, for franchise naming keys | `Verified` in v21 sheet | parent program token |
| `school_slug` | Website/location URL alias | Sometimes, alias only unless reconciled | `Partial` | `school_uuid` |
| `canonical_location_id` | Location ID in warehouse views | Not final yet | `Partial` mixed format | `school_uuid` |
| `location_slug` | Naming/URL/build-control location alias | Use only after mapping to school | `Partial` | `school_uuid` |
| `campaign_slot` | v21 budget-plan row key | Yes, for sheet planning only | `Verified` sheet key | platform campaign ID |
| `copy_template_slot` | Hidden CW template row ID such as `PCT-*` / `FCT-*` | Yes, sheet-internal | `Verified` sheet key | user-facing copy angle |
| `copy_render_slot` | Hidden MB rendered-copy row ID | Yes, sheet-internal | `Verified` sheet key | copy template label |
| `creative_slot` | Hidden GD creative row ID | Yes, sheet-internal | `Verified` sheet key | file name |
| `campaign_key` | Stable naming/UTM key for campaign | Yes, for naming/UTM/reporting | `Partial` until approved for live rows | visible campaign name |
| `ad_set_key` / `ad_group_key` | Stable key for Meta ad set or Google ad group | Yes, for naming/UTM/reporting | `Partial` until approved | visible ad set/ad group name |
| `ad_data_key` | Meta ad-level UTM/content key | Yes, for naming/UTM/reporting | `Partial` until approved | Meta ad ID |
| `ad_build_key` | Google ad build key because ads lack Meta-style names | Yes, for naming/UTM/reporting | `Partial` until approved | Google ad display name |
| `campaign_id` | Platform campaign object ID | Yes, live object handle | `Verified` when read from platform inventory | campaign name |
| `adset_id` | Meta ad set object ID | Yes, live object handle | `Verified` when read from platform inventory | ad set name |
| `ad_id` | Platform ad object ID | Yes, live object handle | `Verified` when read from platform inventory | ad name/build key |
| `customer_id` | Google Ads customer ID | Yes, account handle | `Verified` when read from Google inventory | account alias |
| `asset_group_id` | Google Performance Max asset group ID | Yes, live object handle | `Verified` when read from Google inventory | asset group name |
| `gclid`, `gbraid`, `wbraid`, `fbclid`, `msclkid` | Click identifiers | Yes, attribution/reconciliation when captured | `Partial` by source | UTMs |
| `lead_id` / `cefa_synuma_lead_id` | CRM/business lead identifier | Yes, if returned and persisted | `Partial` | event ID |

## Conversion Event Taxonomy

| Property | Neutral website event | Business truth | GA4 destination | Google Ads destination | Meta destination | Primary bidding status | Status |
|---|---|---|---|---|---|---|---|
| Parent `cefa.ca` | `school_inquiry_submit` | Gravity Forms Form 4 and downstream KinderTales/business delivery | `generate_lead` | Existing primary `Inquiry Submit_ollo` | `Inquiry Submit` on dataset `918227085392601` | Parent final conversion path | `Verified` |
| Franchise Canada `franchise.cefa.ca` | `franchise_inquiry_submit` | Franchise Gravity Form 1 and Synuma/SiteZeus delivery | `generate_lead` | Existing primary `fr_application_submit` | `Fr Application Submit` / `Fr Application Submit_CAD` on shared dataset `918227085392601` | Preserve existing primary action for continuity | `Partial` pending delayed platform confirmation |
| Franchise Canada `franchise.cefa.ca` | `real_estate_site_submit` | Franchise Gravity Form 2 and Synuma/SiteZeus delivery | GA4/reporting mapping | Secondary `fr_site_form_submit` | `Fr Site Form Submit` | Secondary/reporting unless approved | `Partial` |
| Franchise USA `www.franchisecefa.com` | `franchise_inquiry_submit` | USA Franchise Gravity Form 1 and Synuma/SiteZeus delivery | `generate_lead` | Pending mapping to selected primary action, likely existing `Application Submit (USA)` | Standard `Lead` on USA dataset `1531247935333023` | Pending paid-media signoff | `Partial` |
| Franchise USA `www.franchisecefa.com` | `real_estate_site_submit` | USA real-estate/site form and Synuma/SiteZeus delivery | GA4/reporting mapping | Pending or secondary | USA Meta reporting/custom conversion if approved | Reporting/secondary until approved | `Partial` |
| Parent micro-events | `parent_inquiry_cta_click`, `find_a_school_click`, `phone_click`, `email_click`, `form_start`, `form_submit_click`, `validation_error` | No lead created by themselves | GA4/reporting only | Not primary bidding | Not primary bidding | Diagnostic only | `Verified` rule |
| Future server-side / CAPI / MP | Future shared logical event with `event_id` | Form/CRM plus event identity | Future additive path | Future additive path | Future CAPI path | Not active until signed off | `Pending` |

## Naming Convention Taxonomy

| Naming family | Applies to | Current pattern / rule | Stable keys | Status | Owning docs |
|---|---|---|---|---|---|
| Meta NC1 | Current live Meta naming version | Existing approved live naming package | Current names plus platform IDs | `Verified` as current live baseline | [naming README](../40-naming-convention/README.md) |
| Meta NC2 | Proposed Meta rename/build planning | `CEFA | {BudgetScope} | {Activation} | {LocationOrGroup} | META | {Objective} | {Funnel} | {Theme} | {YYYYMM} | {Seq}` | `campaign_key`, `ad_set_key`, `ad_data_key` | `Partial`; not live rename approval | [Meta NC2 inventory](../40-naming-convention/meta-naming-nc2-active-last-30-inventory-2026-05-04.md) |
| Google GADS1 | Proposed Google Ads rename/build planning | `CEFA | {BudgetScope} | {Activation} | {LocationOrGroup} | GOOGLE | {Channel} | {Objective} | {Funnel} | {Theme} | {YYYYMM} | {Seq}` | `campaign_key`, `ad_group_key`, `asset_group_key`, `ad_build_key` | `Partial`; not live rename approval | [Google GADS1 inventory](../40-naming-convention/google-ads-naming-gads1-active-last-30-inventory-2026-05-04.md) |
| Meta ad set | Meta ad set naming | `{Persona} | {AudienceType} | {Geo} | {Placement}` | `ad_set_key` | `Partial` until approved per row | [Meta NC2 inventory](../40-naming-convention/meta-naming-nc2-active-last-30-inventory-2026-05-04.md) |
| Meta ad | Meta ad naming | `{FormatTag} | {ProgramOrTopic} | {VisualConcept} | {CopyAngle} | v{AdVersion}` | `ad_data_key`, `creative_slot`, `copy_render_slot` | `Partial`; many ad proposals need review | [Meta build manifest](../40-naming-convention/meta-creative-build-import-manifest-2026-05-04.md) |
| Google Search ad group | Google Ads Search naming | `{PersonaOrIntent} | {KeywordTheme} | {GeoOrMarket} | {MatchStrategy}` | `ad_group_key` | `Partial` | [Google GADS1 inventory](../40-naming-convention/google-ads-naming-gads1-active-last-30-inventory-2026-05-04.md) |
| Google PMax asset group | Google Ads PMax naming | `Asset Group | {GeoOrMarket} | PMax` | `asset_group_key` | `Partial` | [Google GADS1 inventory](../40-naming-convention/google-ads-naming-gads1-active-last-30-inventory-2026-05-04.md) |
| Parent program token | Parent copy/creative/ad keys | `all`, `cefa_baby`, `jk1`, `jk2`, `jk3`, approved combos | `program_token` | `Verified` in v21 POC; program source reconciliation `Partial` | [v21 build control doc](../40-naming-convention/paid-media-build-control-center-v21-final-poc-2026-05-06.md) |
| Franchise topic | Franchise copy/creative/ad keys | Franchise-specific topic/offer tokens | `franchise_topic`, `offer_type` | `Verified` in v21 POC | [v21 build control doc](../40-naming-convention/paid-media-build-control-center-v21-final-poc-2026-05-06.md) |
| Copy angle | CW/GD/ad data keys | `Attention`, `Interest`, `Desire`, `Action`, `Trust`, `Program Fit`, `Curriculum`, `Safety`, `Convenience`, `Social Proof`, `Urgency`, `Diversification`, `Investment`, `Market Opportunity`, `Real Estate`, `Retargeting` | copy-angle slug in keys | `Verified` in v21 POC | [v21 build control doc](../40-naming-convention/paid-media-build-control-center-v21-final-poc-2026-05-06.md) |
| Local listing UTMs `ll1` | GBP/Yelp parent listing URLs | `utm_source={platform}`, `utm_medium=local_listing`, stable campaign by link intent | `utm_id`, `utm_content` | `Partial` pending full slug/listing field confirmation | [local listing UTM rules](../40-naming-convention/local-listing-utm-rules-gbp-yelp-2026-05-03.md) |

## UTM And Attribution Rules

| Channel | Source | Medium | Campaign | Content | Term | Notes |
|---|---|---|---|---|---|---|
| Meta Ads | `meta` | `paid_social` | `{campaign_key}` | `{ad_data_key}` | `{ad_set_key}` | Use generated keys, not mutable names. |
| Google Ads | `google` | `cpc` | `{campaign_key}` | `{ad_build_key}` | `{keyword_or_ad_group_key}` | Keep auto-tagging and `gclid`; UTMs are reporting fallback/contract. |
| Google Business Profile | `google_business_profile` | `local_listing` | `parents_school_location` or `parents_school_inquiry` | `{school_slug}__website` or `{school_slug}__inquiry_form` | usually blank | Schema version in `utm_id=ll1__gbp__...`. |
| Yelp | `yelp` | `local_listing` | `parents_school_location` or `parents_school_inquiry` | `{school_slug}__website` or `{school_slug}__inquiry_form` | usually blank | Schema version in `utm_id=ll1__yelp__...`. |
| Franchise GAConnector | captured `lc_*` / `fc_*` values | vendor-owned | vendor-owned | vendor-owned | vendor-owned | Preserve and read; do not overwrite until replacement is approved. |

## Question-To-Source Routing

| Question | First source to check | Supporting sources | What not to use as final truth |
|---|---|---|---|
| Did a parent lead happen? | Gravity Forms Form 4 and downstream business delivery | Helper plugin event, GTM/GA4/platform receipt, refreshed BigQuery business-truth marts | Meta/Google/GA4 conversions alone |
| Did a franchise lead happen? | Franchise Gravity Forms entry and Synuma/SiteZeus delivery | Helper event, GTM/GA4/platform receipt, refreshed franchise mart | Platform conversions alone |
| Which school is this parent lead for? | `school_uuid` / `school_selected_id` | `dim_school`, Field 32 payload, school form programs sheet | School label, slug, campaign name alone |
| Which program is this parent lead for? | `program_id` when available | program label, `program_token`, school form programs sheet | Ad copy/program label alone |
| Which campaign/ad object produced traffic? | Platform object IDs and click IDs | active object inventory CSVs, UTMs, BigQuery raw/marts | mutable campaign/ad names alone |
| How should a new campaign/ad/creative be named? | v21 naming sheet and docs/40 naming rules | active object inventories, budget workbook, master data | old platform names as a template |
| What should an executive dashboard show? | BigQuery dashboard/Looker contract views | source freshness docs, rule registry, master-data docs | raw platform rows without freshness and business-truth context |
| What should a local listing URL use? | `ll1` GBP/Yelp UTM rules | school slug crosswalk/master data | paid-media NC2/GADS1 tokens |
| What source should a budget value come from? | OneDrive/SharePoint budget workbook | read-only v21 budget mirror once synced | platform spend pacing math as live budget approval |

## Current Cross-Workstream Gaps

| Gap | Status | Primary owner | Notes |
|---|---|---|---|
| Current parent business-truth marts after 2026-03-29 | `Pending` | Conversion tracking + BigQuery | Needed before dashboards treat current parent inquiry counts as final truth. |
| Current franchise lead-source mart after 2026-03-29 | `Pending` | Conversion tracking + BigQuery | Needed before final franchise reporting and offline exports. |
| Google Ads and Supermetrics detail after 2026-04-30 | `Open question` | Paid media + BigQuery | Recheck before May paid reporting. |
| School-form programs sheet vs 53-row `dim_school` reconciliation | `Partial` | Master data | Sheet has 51 rows; BigQuery has 53 checked rows plus slug differences. |
| `canonical_location_id` normalization | `Pending` | Master data | Present but mixed UUID-like and slug-like values. |
| Platform object rename approvals | `Pending` | Naming + paid media | NC2/GADS1 are planning surfaces, not live rename approval. |
| Fresh Meta/Google import template validation | `Pending` | Naming + paid media | Required before real bulk uploads from v21 sheet. |
| n8n phase-1 validation/export/audit workflow | `Pending` | Naming + automation | Allowed first phase only; no live activation/budget/optimization writes. |
| Rule-registry upload workflow | `Pending` | BigQuery + governance | Table/view exists, but future controlled upload process is not built. |

## Owning Workstream Summary

| Workstream | Owns in this taxonomy | README |
|---|---|---|
| Governance | Source routing, authority order, cross-workstream taxonomy | [docs/00-governance](./README.md) |
| Conversion tracking | Events, payloads, GTM/GA4/Ads/Meta conversion mapping, event IDs, business-truth gaps | [docs/10-conversion-tracking](../10-conversion-tracking/README.md) |
| BigQuery/data | Warehouse surfaces, marts, dashboards, freshness, rule registry, offline export readiness | [docs/20-bigquery](../20-bigquery/README.md) |
| SEO | Search Console, DataForSEO, organic/local SEO measurement and page taxonomy | [docs/30-seo](../30-seo/README.md) |
| Naming convention | Campaign/ad/ad set/ad group naming, creative filenames, UTM conventions, v21 build control | [docs/40-naming-convention](../40-naming-convention/README.md) |
| Paid media | Platform source availability, conversion action usage, launch QA, budget/bidding guardrails | [docs/50-paid-media](../50-paid-media/README.md) |
| Master data | Schools, programs, location IDs, CRM/system crosswalks, reference data | [docs/60-master-data](../60-master-data/README.md) |

## Maintenance Rule

When adding or changing a source:

1. Update the narrow owning workstream doc first.
2. Add or update machine-readable reference data in `data/reference/` only when it is reusable and non-secret.
3. Update this file if the source belongs in the cross-workstream taxonomy.
4. Update [README.md](./README.md) if the governance navigation changes.
5. Keep status labels explicit; do not mark assumptions as verified.
