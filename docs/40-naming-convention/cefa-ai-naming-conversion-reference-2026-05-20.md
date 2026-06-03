# CEFA AI Naming And Conversion Reference

Last updated: 2026-06-03

Audience: AI agents, Codex, ChatGPT, paid media, conversion tracking, content, design, analytics, and n8n automation planning.

Primary purpose: one AI-ready reference for CEFA paid-media naming, creative/copy build rules, UTM rules, page URL rules, and conversion-tracking guardrails.

This file is a consolidated reference, not a replacement for the narrower source-of-truth docs. When rules conflict, use the authority order below and update the narrow owning workstream first.

## 1. Authority Order

Status: `Verified`

Use sources in this order:

1. Live verified systems and current API/browser/network evidence: WordPress, Gravity Forms, GTM, GA4, Google Ads, Meta, BigQuery, CRM exports, Ads Manager, Google Sheets API.
2. Current governed repo docs in this `conversion_tracking` repo.
3. Local CEFA conversion-tracking knowledge base and CEFA NEXUS context when not yet migrated into this repo.
4. Explicit CEFA Ops/source files cited by a repo doc.
5. External platform best practices.

Use these labels in all future work:

| Label | Meaning |
|---|---|
| `Verified` | Confirmed through live system, API, code, BigQuery, or cited source file. |
| `Partial` | Available but incomplete, mixed-format, source-limited, or not fully normalized. |
| `Pending` | Known needed field, test, or decision not confirmed yet. |
| `Open question` | Needs CEFA, agency, platform owner, or source-system confirmation. |
| `Reference only` | Helpful background, not operational truth. |

## 2. Current Human Working Surface

Status: `Verified` for sheet identity and tab list on 2026-06-03.

Current v21 final POC Google Sheet:

```text
CEFA Paid Media Naming Convention Build Control - v21 Final POC - 2026-05-06
https://docs.google.com/spreadsheets/d/15MkgHS4YQLFMAsZDleJytIIsLn-bupUJBELWmykuN6U/edit
Spreadsheet ID: 15MkgHS4YQLFMAsZDleJytIIsLn-bupUJBELWmykuN6U
```

Important sheet tabs currently visible or present:

| Area | Tabs |
|---|---|
| Team guide | `README`, `COPYWRITER_GUIDE` |
| Campaign planning | `CAMPAIGN_PICKER`, `CAMPAIGN_SELECTOR`, `OBJECT_DESTINATIONS` |
| Parent Meta copy/render/build | `PARENT_COPY_CW`, `PARENT_RENDER_MB`, `PARENT_BUILD_MB` |
| Franchise Meta copy/render/build | `FRANCHISE_COPY_CW`, `FRANCHISE_RENDER_MB`, `FRANCHISE_BUILD_MB` |
| Parent/franchise creative | `PARENT_CREATIVE_GD`, `FRANCHISE_CREATIVE_GD`, `CREATIVE_ASSET_REGISTRY_GD`, `CAROUSEL_CARD_MAP` |
| Google copy/build | `GOOGLE_PARENT_RSA_CW`, `GOOGLE_FRANCHISE_RSA_CW`, `GOOGLE_PARENT_BUILD_MB`, `GOOGLE_FRANCHISE_BUILD_MB` |
| Review | `META_STAKEHOLDER_REVIEW`, `GOOGLE_STAKEHOLDER_REVIEW`, `STAKEHOLDER_REVIEW` |
| Import/audit/QA | `META_IMPORT_READY`, `GOOGLE_IMPORT_READY`, `IMPORT_AUDIT`, `QA_REPORT`, `CAMPAIGN_RENAME_REVIEW`, `PIXEL_EVENT_QA` |
| Reference/admin | `SETTINGS_TOKENS`, `LOCATION_TOKEN_MAP`, `SOURCES`, `BUDGET_LSM`, `BUDGET_CORP`, `BUDGET_FRANCHISE`, `META_OBJECT_INVENTORY`, `GOOGLE_ADS_OBJECT_INVENTORY`, `N8N_PLAN` |

The Google Sheet remains the human POC working surface. This Markdown file is the AI briefing surface.

## 3. Release Gate

Status: `Verified`

Current release status:

```text
Internal POC only.
```

Allowed now:

- validation;
- copy rendering;
- QA;
- import-file generation;
- manual platform preview;
- ID sync;
- audit;
- draft-only POC prep.

Not allowed without explicit CEFA/MB approval:

- live activation;
- live budget changes;
- live campaign/ad set/ad/ad group/asset group renames;
- deletion;
- bid strategy changes;
- optimization event changes;
- pixel/dataset changes;
- conversion goal changes;
- direct launch automation.

Default output state:

```text
PAUSED
```

Any imported or API-created Meta or Google object must default to paused unless there is separate explicit approval.

## 4. Naming Versions

| Family | Current status | Meaning |
|---|---|---|
| `NC1` | `Verified` current live Meta naming baseline | Existing approved Meta naming package. Do not silently change token meanings. |
| `NC2` | `Partial` proposed Meta rename/build planning | Planning structure for future Meta naming, UTMs, build manifests, and rename review. Not live rename approval. |
| `GADS1` | `Partial` proposed Google Ads rename/build planning | Planning structure for Google Ads naming, UTMs, Google build keys, and rename review. Not live rename approval. |
| `ll1` | `Partial` local listing UTM version | GBP/Yelp UTM schema. Requires school slug and listing-field confirmation before live bulk changes. |

## 5. Core Object Naming Rules

### Meta Campaign

Status: `Partial` for future rename/build planning.

```text
CEFA | {BudgetScope} | {Activation} | {LocationOrGroup} | META | {Objective} | {Funnel} | {Theme} | {YYYYMM} | {Seq}
```

Example structure:

```text
CEFA | LSM | Enrollment | Markham | META | LEADS | BOF | Enrollment | 202506 | 001
```

### Meta Ad Set

Status: `Partial`

```text
{Persona} | {AudienceType} | {Geo} | {Placement}
```

Example:

```text
Prospective Parents | Broad | Markham | Advantage+
```

### Meta Ad

Status: `Partial`

```text
{FormatTag} | {ProgramOrTopic} | {VisualConcept} | {CopyAngle} | v{AdVersion}
```

Example:

```text
IMG | All Programs | Markham | Attention | v1
```

### Google Ads Campaign

Status: `Partial`

```text
CEFA | {BudgetScope} | {Activation} | {LocationOrGroup} | GOOGLE | {Channel} | {Objective} | {Funnel} | {Theme} | {YYYYMM} | {Seq}
```

Example:

```text
CEFA | LSM | Enrollment | Oakville | GOOGLE | SEARCH | LEADS | BOF | Enrollment | 202604 | 001
```

### Google Search Ad Group

Status: `Partial`

```text
{PersonaOrIntent} | {KeywordTheme} | {GeoOrMarket} | {MatchStrategy}
```

### Google Performance Max Asset Group

Status: `Partial`

```text
Asset Group | {GeoOrMarket} | PMax
```

### Google Ad Build Key

Status: `Partial`

Google Ads ads do not have a normal Meta-style visible ad name. Use `ad_id` plus a generated build key.

```text
{campaign_key}__{ad_group_or_asset_group_key}__{copy_angle_slug}__ad-v{#}__gads1
```

## 6. Stable IDs And Keys

Status: `Verified` as a rule.

Never use mutable names as the only join handle.

| Layer | Stable/live handle | Naming/build key |
|---|---|---|
| Meta account | `account_id` | `account_alias` |
| Meta campaign | `campaign_id` | `campaign_key` |
| Meta ad set | `adset_id` | `ad_set_key` |
| Meta ad | `ad_id` | `ad_data_key` |
| Google account | `customer_id` | `account_alias` |
| Google campaign | `campaign_id` | `campaign_key` |
| Google search ad group | `ad_group_id` | `ad_group_key` |
| Google PMax asset group | `asset_group_id` | `asset_group_key` |
| Google ad | `ad_id` | `ad_build_key` |
| v21 budget plan | `campaign_slot` | generated campaign picker/key |
| v21 content row | `copy_template_slot` | generated copy key |
| v21 rendered row | `copy_render_slot` | generated rendered copy key |
| v21 creative row | `creative_slot` | generated creative key/filename |
| Parent school | `school_uuid` | school slug only as alias |
| Conversion event | `event_id` | never use school/program/location IDs as event IDs |

Rules:

- `campaign_slot` is a sheet planning key, not a platform campaign ID.
- `program_label` is human-facing.
- `program_token` is naming/UTM-safe.
- `franchise_topic` is for franchise copy/creative/ad keys and should not be replaced by parent program tokens.
- `school_slug` is useful for URLs and UTMs, but `school_uuid` is the stronger parent school join key.

## 7. Budget Scope And Business Line Separation

Status: `Verified` as a workbook rule.

Keep parent LSM, parent corporate, and franchise separated.

| Budget/business scope | Use |
|---|---|
| `LSM` | Local school marketing, school/location-specific parent ads. |
| `CORP` | Parent corporate campaigns or multi-location/group campaigns. |
| `FRANCHISE` | Franchise acquisition and franchise/site inquiry campaigns. |

Rules:

- Do not mix parent program tokens into franchise rows.
- Do not mix Google Search/RSA copy into Meta copy tabs.
- Do not mix Google build rows into Meta build tabs.
- Budget tabs are reference-only mirrors/sources, not live platform budget instructions.
- The canonical CEFA budget workbook remains the OneDrive/SharePoint budget workbook; v21 budget tabs are planning/reference surfaces only.

## 8. Parent Program Tokens

Status: `Verified` in v21 POC; source reconciliation `Partial`.

| Human label | Machine token | Use |
|---|---|---|
| All Programs | `all` | Parent ads/copy/creative for CEFA Baby, JK1, JK2, and JK3 together. |
| CEFA Baby | `cefa_baby` | CEFA Baby-specific parent copy/creative. |
| Junior Kindergarten 1 / JK1 | `jk1` | JK1-specific parent copy/creative. |
| Junior Kindergarten 2 / JK2 | `jk2` | JK2-specific parent copy/creative. |
| Junior Kindergarten 3 / JK3 | `jk3` | JK3-specific parent copy/creative. |
| CEFA Weekend Care Program | `weekend_care` | Special program seen for Calgary Cornerstone in the school-form source. |

Approved combo tokens such as `jk1+jk2` or `jk2+jk3` can be used only when CEFA approves the combination.

## 9. Copy Angle Tokens

Status: `Verified` in v21 POC.

Approved `CopyAngle` dropdown values:

```text
Attention
Interest
Desire
Action
Trust
Program Fit
Curriculum
Safety
Convenience
Social Proof
Urgency
Diversification
Investment
Market Opportunity
Real Estate
Retargeting
```

For the first parent LSM POC, `Attention` is the working copy angle.

## 10. Creative Naming And Minimum Designer Input

Status: `Verified` for workbook direction; `Partial` for platform asset sync.

Designers should not manually build platform names. They should fill practical creative fields and let the sheet generate filenames/keys.

Minimum LSM designer input for a simple Meta creative row:

| Field | Why it matters |
|---|---|
| `location_or_market` | Shows which school/location the creative supports. |
| `program_label` or `franchise_topic` | Distinguishes parent programs from franchise topics. |
| `format` | Example: `IMG`, `VID`, `CAR`. |
| `aspect_ratio` / size | Example: `1x1`, `4x5`, `9x16`, `1.91x1`. |
| `visual_concept` | The creative idea/theme, for example `Accepting Applications`. |
| `copy_angle` | Connects the asset to Attention, Curriculum, Convenience, etc. |
| `version` | Example: `v1`. |
| `file_type` | Example: `jpg`, `png`, `mp4`. |
| `file_url` or local/SharePoint/Drive reference | Required before upload/import. |
| `approval_status` | Must be approved before import-ready output. |

Creative group key pattern:

```text
{school_slug}__{scope}__{funding}__{activation}__{theme}__{format}__{concept}__cr##__v#
```

Rules:

- File identity and platform asset identity are separate.
- Meta image hash, Meta video ID, Google asset ID, and YouTube ID remain blank until platform upload/export sync.
- Do not use raw Drive/SharePoint filenames as visible Meta ad names.
- Carousel is one ad with card/product columns, not automatically separate ads.

## 11. Copywriter And Reviewer Rules

Status: `Verified`

Content writers:

- Use `PARENT_COPY_CW` and `FRANCHISE_COPY_CW` for Meta copy.
- Use `GOOGLE_PARENT_RSA_CW` and `GOOGLE_FRANCHISE_RSA_CW` for Google RSA copy.
- Start from `location_or_market`.
- Do not type `copy_template_slot` or `copy_template_key`; those are generated/hidden.
- For April/May 2026 POC work, use direct location/program-specific copy instead of forcing placeholders.

MB/media:

- Use `PARENT_RENDER_MB` or `FRANCHISE_RENDER_MB`.
- Select `month`, `location_or_market`, and readable `copy_template_picker`.
- Hidden slot IDs drive formulas.

Reviewers:

- Use `META_STAKEHOLDER_REVIEW` for Meta primary text, headline, description, CTA.
- Use `GOOGLE_STAKEHOLDER_REVIEW` for Google RSA headlines, descriptions, and paths.
- The old `STAKEHOLDER_REVIEW` tab is an index only.

## 12. Paid Media UTM Rules

Status: `Verified` as current contract; row-level keys are `Partial` until approved per build.

### Meta Ads

```text
utm_source=meta
utm_medium=paid_social
utm_campaign={campaign_key}
utm_content={ad_data_key}
utm_term={ad_set_key}
```

### Google Ads

```text
utm_source=google
utm_medium=cpc
utm_campaign={campaign_key}
utm_content={ad_build_key}
utm_term={keyword_or_ad_group_key}
```

Rules:

- Use generated keys, not mutable visible names.
- Keep Google Ads auto-tagging and `gclid` where currently used. UTMs are a reporting fallback/contract, not a replacement for click IDs.
- Destination URL and URL tags must stay as separate fields.
- Do not backfill historical reporting by name alone.

## 13. Local Listing UTM Rules: GBP And Yelp

Status: `Partial`

Version:

```text
ll1
```

Local listing tokens:

| Field | Google Business Profile | Yelp |
|---|---|---|
| `utm_source` | `google_business_profile` | `yelp` |
| `utm_medium` | `local_listing` | `local_listing` |
| platform short token | `gbp` | `yelp` |

Website link rule:

```text
utm_source={platform}
utm_medium=local_listing
utm_campaign=parents_school_location
utm_content={school_slug}__website
utm_id=ll1__{platform_short}__{school_slug}
```

Inquiry-intent link rule:

```text
utm_source={platform}
utm_medium=local_listing
utm_campaign=parents_school_inquiry
utm_content={school_slug}__inquiry_form
utm_id=ll1__{platform_short}__{school_slug}__inquiry
```

Important URL caveat:

- Older local-listing examples used `/cefa-find-a-school/{school_slug}/`.
- The current parent school/form source includes `School URL` and `Inquiry Form URL` and the live parent inquiry pattern uses `https://cefa.ca/submit-an-inquiry-today/?location={school_slug}`.
- Before bulk GBP/Yelp updates, confirm the current school page URL and available listing fields per location.

Do not use paid media tokens such as `LSM`, `META`, `BOF`, `IMG`, `VID`, or `CAR` in GBP/Yelp UTMs.

## 14. Parent Page URL And Inquiry URL Rules

Status: `Partial`

Current parent URL patterns seen in governed docs and live samples:

```text
School page:
https://cefa.ca/school/{school_slug}/

Parent inquiry form:
https://cefa.ca/submit-an-inquiry-today/?location={school_slug}
```

Examples:

```text
https://cefa.ca/school/kelowna-spall/
https://cefa.ca/submit-an-inquiry-today/?location=abbotsford-highstreet
```

Rules:

- For parent lead campaigns, use the inquiry form URL when the intended action is an inquiry form submission.
- For school-page traffic or local listing context, use the verified school page URL for the specific school.
- Keep `?location={school_slug}` when a school-specific inquiry CTA must preserve school context.
- Do not assume the old `/cefa-find-a-school/{slug}/` pattern without verifying the live school/form source.
- Use the `CEFA School Form Programs` sheet and `dim_school` reconciliation before a bulk URL rollout.

School form source:

```text
CEFA School Form Programs
https://docs.google.com/spreadsheets/d/1CFWM84XT0NGTlaJkg5NjUxCjQZMnxd0Fy5G6SfdPACc/edit
```

Known source status:

- `Verified`: sheet is readable in prior check.
- `Partial`: sheet has 51 data rows, while checked BigQuery `dim_school` has 53 rows.
- `Open question`: some slug differences remain, including `langley-city-centre` vs `langley-city-center`, `vancouver-ubc` vs `ubc`, and `south-surrey-panorama` vs warehouse variants.

## 15. Build Manifest Rules

Status: `Verified` as required structure; `Partial` as live import implementation.

Every importable row must map:

- action;
- account;
- platform;
- destination IDs;
- campaign/ad set/ad group/asset group/ad keys;
- budget group/reference;
- location/school;
- parent program token or franchise topic;
- copy key/rendered copy;
- creative key/file/asset identity;
- destination URL;
- UTM fields;
- generated names;
- status fields;
- QA status;
- approval status;
- audit fields.

Allowed build actions:

| Action | Required IDs before export |
|---|---|
| `rename_campaign` | `campaign_id` |
| `rename_adset` | `campaign_id`, `adset_id` |
| `rename_ad` | `campaign_id`, `adset_id`, `ad_id` |
| `create_ad` | `campaign_id`, `adset_id`; `ad_id` blank until post-import sync |
| `update_ad` | `campaign_id`, `adset_id`, `ad_id` |
| `create_adset` | `campaign_id`; `adset_id` blank until post-import sync |
| `create_campaign` | separate stronger approval because budget/objective/settings risk is higher |
| `pause_only` | target object ID |

Import-ready gates:

- `qa_status=OK`;
- `approval_status=Approved`;
- status is `PAUSED`;
- required IDs are present for the action;
- no unresolved placeholders;
- destination URL and URL tags are valid;
- creative/copy are present and approved;
- no selected inventory row is marked `needs_review`;
- duplicate keys/names are blocked within the batch.

## 16. Meta Bulk Import Rules

Status: `Verified` for successful 2026-05-05 franchise video add-only import pattern; `Pending` for next template validation.

Reusable Meta pattern:

1. Start from a fresh Ads Manager export/import schema.
2. Keep generated import files UTF-16 tab-delimited when required by Ads Manager, even if extension is `.csv`.
3. For create-ad rows under existing objects, populate Campaign ID and Ad Set ID.
4. Leave Ad ID blank for add-only new ads.
5. Set every new ad row to `PAUSED`.
6. Mirror live campaign/ad set status values immediately before upload.
7. Preserve existing campaign/ad set names unless the batch is explicitly a rename batch.
8. Put destination URLs in `Link`.
9. Put tracking in `URL Tags`.
10. Use Ads Manager bulk import preview before accepting import.
11. Export after import and reconcile IDs, statuses, add-ons, tags, and URL tags.

Do not treat a successful paused import as approval to activate ads.

## 17. Google Ads Bulk Rules

Status: `Partial`

Google Ads needs a Google-specific manifest. Do not use the Meta import manifest for Google.

Search/RSA rows need Google-specific fields:

- `customer_id`;
- `campaign_id`;
- `ad_group_id`;
- `ad_id` only when updating;
- keyword theme;
- match strategy;
- final URL;
- final URL suffix / tracking template inputs;
- up to 15 RSA headlines;
- up to 4 RSA descriptions;
- path 1 and path 2;
- generated `ad_build_key`;
- QA, approval, and paused status.

PMax rows need:

- `customer_id`;
- `campaign_id`;
- `asset_group_id`;
- asset group key;
- final URL;
- asset references;
- business name;
- headlines/descriptions/images/logos/videos;
- QA, approval, and paused status.

No live Google campaign, ad group, asset group, ad, budget, bidding, status, conversion-action, or tracking-template change is approved by this reference.

## 18. Active Object Inventories

Status: `Verified` for API reads; proposed names `Partial`.

Meta inventory:

```text
docs/40-naming-convention/meta-naming-nc2-active-last-30-inventory-2026-05-04.md
data/reference/cefa-meta-active-object-inventory-2026-04-05-to-2026-05-04.csv
```

Scope:

- CEFA Early Learning / parent;
- CEFA Franchisor / franchise;
- delivery window `2026-04-05` through `2026-05-04`;
- 21 parent campaigns, 31 parent ad sets, 133 parent ads;
- 4 franchise campaigns, 9 franchise ad sets, 64 franchise ads.

Google Ads inventory:

```text
docs/40-naming-convention/google-ads-naming-gads1-active-last-30-inventory-2026-05-04.md
data/reference/cefa-google-ads-active-object-inventory-2026-04-05-to-2026-05-04.csv
```

Scope:

- CEFA $3000 / parent;
- CEFA Franchisor / franchise;
- delivery window `2026-04-05` through `2026-05-04`;
- 19 parent campaigns, 76 parent search ad groups, 3 parent PMax asset groups, 97 parent ads;
- 3 franchise campaigns, 9 franchise ad groups, 1 franchise PMax asset group, 13 franchise ads.

Rules:

- Use inventories for ID-backed rename/build planning.
- Proposed NC2/GADS1 names are not live rename approval.
- Do not use rows marked `needs_review` for final naming without review.
- Keep old/current names and proposed names as labels, not primary join keys.

## 19. Current POC Examples

Status: `Verified` for sheet source rows; live Ads Manager execution was not completed in the governed doc.

### Kelowna Spall Attention Copy

```text
PARENT_COPY_CW row: PCT-005
location_or_market: Kelowna - Spall
copy_angle: Attention
program_label: All Programs
offer_type: application-submit
cta: LEARN_MORE
approval_status: Draft
```

Rule:

- This row is direct location copy.
- Do not reintroduce `{CityName}` or `{SchoolName}` placeholders for this row.

### Markham Attention Draft POC Source

```text
PARENT_COPY_CW row: PCT-012
PARENT_RENDER_MB row: PR-003
PARENT_CREATIVE_GD rows: PCTRV-001 through PCTRV-003
PARENT_BUILD_MB batch: markham_attention_poc_20260508
Target campaign ID: 120229052675680400
Target ad set ID: 120229052675670400
Target ad name: IMG | All Programs | Markham | Attention | v1
```

Rules:

- Keep Markham work draft-only unless MB explicitly approves publish.
- Verify selected Ads Manager campaign/ad set IDs before editing any draft.
- Do not publish from Ads Manager without explicit approval.

## 20. Conversion Tracking: Parent Site

Status: `Verified` for the current helper-plugin, GTM, GA4, and Google Ads contract. Meta `Inquiry Submit` is active in the documented destination path; continue monitoring Events Manager/deduping details before treating Meta server-side quality as fully signed off.

Property:

```text
cefa.ca
```

Primary form:

```text
Gravity Forms Form 4
```

Neutral website event:

```text
school_inquiry_submit
```

Business truth:

```text
Gravity Forms Form 4 submission and downstream KinderTales/business delivery
```

Destination mapping:

| Destination | Current mapping |
|---|---|
| GTM | `GTM-NZ6N7WNC` |
| GA4 | `G-T65G018LYB` / property `267558140`, destination event `generate_lead` |
| Google Ads | `AW-802334988/cFt-CMrLufgCEIzSyv4C`, existing action `Inquiry Submit_ollo` |
| Meta | dataset/pixel `918227085392601`, event `Inquiry Submit` |

Parent helper/plugin rules:

- Live plugin documented as `cefa-conversion-tracking` version `0.4.3`.
- Helper-plugin dataLayer event is the final browser conversion source.
- Gravity Forms Google Analytics Add-On is not the final conversion source.
- Thank-you pageviews are not final conversion sources.
- One successful Form 4 submission should create one final `school_inquiry_submit`.
- Direct thank-you reload/visit should not create a final conversion.

Important Field 32 values:

| Field | Meaning |
|---|---|
| `32.1` | school UUID |
| `32.2` | program ID |
| `32.3` | days per week |
| `32.4` | event ID |
| `32.5` | school slug |
| `32.6` | school name |
| `32.7` | program name |

Attribution fields:

```text
35-46
```

Use for UTM/click-ID/first-touch handoff.

Parent micro-events:

```text
parent_inquiry_cta_click
find_a_school_click
phone_click
email_click
form_start
form_submit_click
validation_error
```

Micro-event rule:

- Reporting/diagnostic only.
- Do not use for primary bidding unless CEFA explicitly changes that rule.
- Do not accept Google Ads suggested click/application conversions such as `Application Click_Discovery`, `Inquiry Click_Discovery`, `Inquiry Click_Weekend/Evening care`, `Inquiry Click_Click_Baby/JK`, `Application Click_Baby/JK`, or `Application Click_Weekend/Evening care` as parent Phase 1A final conversions. If CEFA later wants click-intent conversions, create them deliberately as secondary/non-bidding events from the helper-plugin event family.

## 21. Conversion Tracking: Franchise Canada

Status: `Partial` / directionally ready. The website helper event, GTM Version `54`, GA4 browser path, Google Ads primary continuity path, and Meta script execution are documented. Delayed platform-reporting and Meta Events Manager confirmation should still be checked before aggressive spend decisions.

Property:

```text
franchise.cefa.ca
```

Primary inquiry event:

```text
franchise_inquiry_submit
```

Real estate/site event:

```text
real_estate_site_submit
```

Destination mapping:

| Destination | Current mapping |
|---|---|
| GTM | `GTM-TPJGHFS` |
| GA4 | `G-6EMKPZD7RD`, destination event `generate_lead` |
| Google Ads inquiry | `AW-11088792613/cys-CIHslY4YEKWYxqcp`, existing primary `fr_application_submit` |
| Google Ads site form | `AW-11088792613/vq7GCIrslY4YEKWYxqcp`, secondary `fr_site_form_submit` |
| Meta | shared dataset `918227085392601`, `Fr Application Submit` / custom conversion `Fr Application Submit_CAD` ID `1146840919855743` |

Business truth:

```text
Franchise Gravity Forms entry and Synuma/SiteZeus delivery
```

Rules:

- Preserve existing `fr_application_submit` continuity unless paid media approves a change.
- Keep real estate/site form as secondary unless explicitly approved for bidding.
- Preserve GAConnector attribution behavior for now.
- Do not create duplicate final conversions.
- Treat form-start/clicker events such as `franchise_form_start` as GA4/reporting micro-conversions only. They are not currently the final franchise inquiry conversion.

## 22. Conversion Tracking: Franchise USA

Status: `Partial`. The helper-event source, GA4 mapping, USA Meta dataset split, USA Meta `Lead` path, and USA custom conversion are documented. Google Ads final helper-submit mapping remains pending.

Property:

```text
www.franchisecefa.com
franchisecefa.com
```

Canonical URL behavior:

```text
www.franchisecefa.com redirects/canonicalizes to franchisecefa.com
```

Primary inquiry event:

```text
franchise_inquiry_submit
```

Real estate/site event:

```text
real_estate_site_submit
```

Destination mapping:

| Destination | Current mapping |
|---|---|
| GTM | `GTM-5LZMHBZL`, documented through Version `18` for USA Meta Lead reliability and Version `19` for GAConnector hidden-field writer behavior |
| GA4 | `G-YL1KQPWV0M`, destination event `generate_lead` |
| Meta | USA dataset `1531247935333023`, standard event `Lead` |
| Meta custom conversion | `1915200622465036` / `USA Franchise Lead`, standard `Lead` plus `/inquiry-thank-you/` |
| Google Ads | final helper-submit mapping pending; likely existing primary `Application Submit (USA)` if approved |

Business truth:

```text
USA franchise Gravity Forms entry and Synuma/SiteZeus delivery
```

Rules:

- Keep USA Meta dataset separate from parent/Canada shared dataset.
- Disable or prove audit-only the USA Gravity Forms Google Analytics Form 1 feed before final signoff.
- Do not let the Gravity Forms GA add-on become a second final conversion source.
- Confirm USA Google Ads bidding account and final primary action before optimization changes.

## 23. Conversion Event Identity And Dedupe Rules

Status: `Verified`

Rules:

- `event_id` is the unique successful conversion-event identity.
- Never use school UUID, school slug, program ID, location ID, campaign ID, or click ID as `event_id`.
- Website events should remain neutral. GTM maps them to platform events.
- Do not send PII or high-cardinality values to GA4, Google Ads, Meta, or dataLayer.
- Do not register full URLs, referrers, click IDs, or event IDs as GA4 custom dimensions unless a governed reason exists.
- Measurement Protocol, CAPI, collector, and server-side GTM are future/additive only until browser parity and dedupe rules are signed off.

## 24. Business Truth Vs Platform Reporting

Status: `Verified` as a rule.

| Question | First source |
|---|---|
| Did a parent lead happen? | Gravity Forms Form 4 and downstream business delivery. |
| Did a franchise lead happen? | Franchise Gravity Forms entry and Synuma/SiteZeus delivery. |
| Which school is a parent lead for? | `school_uuid` / `school_selected_id`, then `dim_school`. |
| Which program is a parent lead for? | `program_id`, then program label/token. |
| Which ad object produced traffic? | Platform object IDs and click IDs, supported by UTMs. |
| How should a new campaign/ad be named? | v21 naming sheet plus this naming reference. |

Rules:

- GA4, Meta, and Google Ads conversions are platform reporting signals, not final business truth alone.
- CRM/business delivery is not replaced by the tracking plugin.
- BigQuery can reconcile source evidence, but it does not replace form/CRM truth.

## 25. n8n Phase Rules

Status: `Pending`

Allowed in n8n phase 1:

- validate sheet rows and controlled values;
- render final copy;
- generate names, keys, URLs, and URL tags;
- generate Meta/Google import files;
- write QA reports;
- notify reviewers/approvers;
- sync returned IDs after manual import or approved paused API creation;
- write import audit rows.

Blocked without explicit approval:

- activate campaigns/ad sets/ad groups/asset groups/ads;
- change live budgets;
- delete objects;
- change optimization goals;
- change attribution settings;
- change conversion events;
- change pixels/datasets;
- create active objects;
- run direct API launch workflows.

## 26. AI Agent Operating Rules

Status: `Verified`

When an AI is asked to create or review naming:

1. Use the v21 Google Sheet as the current human build/control surface.
2. Use this file as the compact AI context.
3. Use the narrow source docs for details.
4. Keep parent, franchise, Meta, and Google separated.
5. Always include platform IDs for live joins or proposed rename/build rows.
6. Treat names as labels, not stable identifiers.
7. Default any import/API-created object to paused.
8. Do not change budgets, activation, optimization events, conversion settings, pixels, datasets, or live names without explicit approval.
9. Mark uncertain facts as `Partial`, `Pending`, or `Open question`.
10. Update the narrowest correct repo doc when a rule changes.

## 27. Key Source Docs

Primary naming docs:

- `docs/40-naming-convention/README.md`
- `docs/40-naming-convention/paid-media-build-control-center-v21-final-poc-2026-05-06.md`
- `docs/40-naming-convention/meta-naming-nc2-active-last-30-inventory-2026-05-04.md`
- `docs/40-naming-convention/google-ads-naming-gads1-active-last-30-inventory-2026-05-04.md`
- `docs/40-naming-convention/meta-creative-build-import-manifest-2026-05-04.md`
- `docs/40-naming-convention/meta-bulk-import-success-pattern-2026-05-05.md`
- `docs/40-naming-convention/local-listing-utm-rules-gbp-yelp-2026-05-03.md`

Primary conversion docs:

- `docs/10-conversion-tracking/event-ownership-matrix-2026-05-05.md`
- `docs/10-conversion-tracking/parent-current-state-and-remaining-work-2026-05-04.md`
- `docs/10-conversion-tracking/parent-tag-assistant-preview-and-meta-restore-plan-2026-05-05.md`
- `docs/10-conversion-tracking/live-main-conversion-event-audit-2026-05-04.md`
- `docs/10-conversion-tracking/franchise-ca-usa-tracking-status-2026-05-03.md`

Primary governance/master-data docs:

- `docs/00-governance/source-of-truth-rules.md`
- `docs/00-governance/agent-responsibilities.md`
- `docs/00-governance/data-taxonomy.md`
- `docs/60-master-data/school-form-programs-google-sheet-source-2026-05-04.md`
- `docs/60-master-data/school-dimension-warehouse-coverage-2026-05-03.md`

## 28. Open Items

Status: `Pending` / `Open question`

- Validate v21 Meta and Google import outputs against fresh Ads Manager and Google Ads Editor templates.
- Run one approved parent LSM POC from copy + creative + build manifest to paused import preview/import.
- Reconcile post-import IDs into `IMPORT_AUDIT`.
- Confirm final URL patterns for all parent school/listing use cases before bulk URL changes.
- Reconcile school-form sheet slugs with `dim_school`.
- Monitor parent Meta `Inquiry Submit` Events Manager/deduping quality and keep the helper-plugin event as the only parent final browser source.
- Confirm Canada franchise delayed platform reporting and Meta Events Manager receipt for `Fr Application Submit`.
- Confirm USA Google Ads final helper-submit mapping and duplicate-source cleanup.
- Confirm ongoing USA Meta Events Manager `Lead` receipt on dataset `1531247935333023` and campaign optimization selection.
- Build machine-readable reference tables only after the human rules above are stable.
