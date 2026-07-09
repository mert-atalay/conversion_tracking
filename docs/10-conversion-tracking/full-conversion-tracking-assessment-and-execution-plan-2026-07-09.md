# Full Conversion Tracking Assessment And Execution Plan

Last updated: 2026-07-09

Scope update, 2026-07-09:

- Consent/CMP implementation is deferred by owner decision and is not part of the current remediation blueprint.
- A partner agency marker is not required for the current Meta comparison. The partner campaign may continue to optimize to the existing broad `USA Franchise Lead` custom conversion and be reported by campaign/ad-set ID. The in-house marker remains required because the in-house custom conversion explicitly filters on it.
- The execution-grade implementation plan is maintained in `cefa-conversion-tracking-remediation-blueprint-2026-07-09.md`.

## Executive Decision

CEFA has a workable confirmed-submit foundation, but it does not yet have one reliable end-to-end attribution contract from ad click to form entry to CRM outcome.

The recommended direction is to build a CEFA-owned attribution bridge, not a general-purpose GAConnector clone. It should capture a small approved acquisition contract at the first-party website layer, preserve first and last non-direct touch, write explicit hidden fields, enforce a unique server event ID, pass that identity into CRM, and reconcile every destination from the saved form entry.

Do not replace the existing production signals in one release. Run the owned bridge beside GAConnector in shadow mode, prove parity, then cut over one property at a time.

## Audit Scope

| Area | Included |
|---|---|
| Websites | `cefa.ca`, `franchise.cefa.ca`, `franchisecefa.com` |
| Forms | Parent Gravity Forms Form 4; Franchise Canada and USA Forms 1 and 2 |
| Website tracking | CEFA Conversion Tracking plugin `0.4.5`, live franchise WPCode bridge, GAConnector field writers |
| Tag management | Parent GTM `GTM-NZ6N7WNC`; Canada GTM `GTM-TPJGHFS`; USA GTM `GTM-5LZMHBZL` |
| Analytics | Parent GA4 `267558140`; Canada GA4 `259747921`; USA GA4 `519783092` |
| Paid destinations | Google Ads `4159217891` and `3820636025`; Meta Ads `1595846967472729` and `505300888223754` |
| Meta datasets | Shared parent/Canada `918227085392601`; USA `1531247935333023` |
| Business and warehouse evidence | Gravity Forms, Form 4 collector, GreenRope attribution, franchise form mart, GA4 export, Google Ads API, Meta Graph/MCP |

Complete-day reporting evidence uses 2026-07-08 as the cutoff. Live configuration, dataset freshness, and controlled-test evidence were checked on 2026-07-09.

This was a read-only platform audit. No GTM container, WordPress site, GA4 property, ad account, campaign, conversion action, dataset, or CRM record was changed.

## Overall Status

| Layer | Status | Decision |
|---|---|---|
| Neutral confirmed-submit events | Good | Keep `school_inquiry_submit`, `franchise_inquiry_submit`, and `real_estate_site_submit`. |
| Parent saved attribution | Partial | Core UTM/click fields save well, but the newer multi-touch model is browser-only and event IDs are not fully unique. |
| Franchise saved attribution | Partial | GAConnector fields save on most entries, but first/last touch does not reach the warehouse correctly and key identifiers are missing. |
| Parent GTM/GA4/Ads/Meta | Partial | Final events are live. GA4 key-event hygiene, source-control drift, and parent GTM API access need repair. |
| Franchise Canada destinations | Partial-good | Confirmed submit reaches GA4, Google Ads, and Meta. Enhanced-conversion selectors are obsolete and micro-goal clutter remains. |
| Franchise USA destinations | Critical gap | GA4 and Meta final-submit paths work. The Google Ads campaign optimizes to a conversion whose live GTM submit tag is paused. |
| Meta agency test | Working with asymmetric reporting contract | In-house uses its marker-filtered conversion. Partner intentionally uses the broad USA inquiry conversion and is separated by campaign/ad-set attribution. |
| Server collection | Good with resilience gap | Parent collector has complete observed post-launch event-ID coverage, but its sender has no retry or delivery ledger. |
| CRM identity | Critical gap | No stable `event_id` is carried from every saved form through GreenRope/Synuma/SiteZeus for deterministic lifecycle joins. |
| Consent | Deferred by owner decision | The audit finding remains recorded, but CMP/Consent Mode work is outside the current remediation blueprint. |
| Warehouse reconciliation | Partial | Form and collector truth are current. The GA4 column in the Form 4 reconciliation table is incorrectly zero. |
| Tests and source control | Critical operational gap | Production code and live GTM state are ahead of `origin/main`; runtime behavior has no automated unit/integration test suite. |

## What Is Working

### Confirmed-submit ownership

- Parent Form 4 emits `school_inquiry_submit` only after a saved Gravity Forms entry.
- Franchise Form 1 emits `franchise_inquiry_submit` and Form 2 emits `real_estate_site_submit`.
- Canada GTM Version 54 disables the old thank-you-page submit trigger with an impossible URL and routes the helper event through one delayed dispatch.
- USA GTM Version 22 keeps legacy destination tags paused and routes the current helper events to GA4 and the USA Meta dataset.
- Event IDs are present on all 6,424 checked parent form rows.

### Parent form and collector coverage

From 2026-05-01 through 2026-07-08, excluding test rows:

| Evidence | Result |
|---|---:|
| Parent Form 4 submissions | 6,424 |
| Event ID present | 6,424 / 100% |
| Source present | 4,111 / 64.0% |
| Medium present | 4,088 / 63.6% |
| Campaign present | 4,067 / 63.3% |
| First landing page present | 6,423 / 99.98% |
| First referrer present | 6,423 / 99.98% |
| `gclid` present | 1,149 |
| `gbraid` present | 835 |
| `wbraid` present | 115 |
| `fbclid` present | 846 |
| Saved `fbp` / `fbc` | 0 / 0 |

After the collector began at 2026-06-13 05:30:41 UTC, every distinct Form 4 event ID in the checked window was present in the collector. This is strong observed delivery evidence. It does not remove the need for retries because the current sender is still fire-and-forget.

### Google Ads campaign goal isolation

- All three active regional parent PMax campaigns use campaign-level goals with only `SUBMIT_LEAD_FORM / WEBSITE` biddable.
- Their active asset groups use `https://cefa.ca/find-a-school/`.
- Active Franchise Canada Ontario and Alberta campaigns use custom goal `CEFA Franchise Application Submit`, containing only `fr_application_submit`.
- Active franchise USA campaign `23533022812` uses custom goal `USA Submit form`, containing only `Application Submit (USA)`.
- Google Ads auto-tagging is enabled in both accounts.

### Meta final conversion rules

- Parent conversion ad sets generally optimize to confirmed custom event `Inquiry Submit`; traffic/open-house ad sets intentionally optimize to landing-page views.
- Canada conversion ad sets use `Fr Application Submit` or custom conversion `Fr Application Submit_CAD`.
- Both active in-house USA ad sets optimize to custom conversion `36521415357505819`, which requires:
  - standard event `Lead`;
  - URL containing `inquiry-thank-you`;
  - `cefa_agency_test=fr_us_in_house`.
- The controlled in-house test fired the broad USA conversion and the in-house conversion once, with matching browser/server event identity.
- Submit-a-site events do not satisfy the USA inquiry custom-conversion URL rule.

### Active ad URL coverage

- All 54 active parent Meta ads have `utm_source`, `utm_medium`, `utm_campaign`, and `utm_content` evidence.
- All 42 active franchise Meta ads have those same UTM fields.
- All 12 active in-house USA ads can resolve the in-house marker:
  - 3 use an explicit `cefa_agency_test` URL parameter;
  - 9 use the exact allowlisted in-house campaign ID/slug fallback in USA GTM Version 22.
- Google Ads account-level tracking templates provide source, medium, campaign ID, creative ID, and keyword when an ad-level suffix is absent.

## Priority Findings

### P0. USA Google Ads is optimizing to a conversion with no live submit tag

Evidence:

- Active USA campaign `23533022812` uses `MAXIMIZE_CONVERSIONS` and custom goal `USA Submit form`.
- The goal contains primary action `7482298930` / `Application Submit (USA)`.
- That action's destination is `AW-11088792613/fnFOCLKk6-8bEKWYxqcp`.
- USA GTM tag 218 has that exact ID/label but is paused and tied to a legacy trigger.
- All other Google Ads final-submit tags in USA GTM are also paused.
- The action had zero conversions from 2026-06-09 through 2026-07-08.

Required repair:

1. Create a new, narrowly named Google Ads conversion tag for the existing action.
2. Fire it only on `cefa_franchise_us_inquiry_dispatch`.
3. Set transaction ID to the server-confirmed `event_id`.
4. Preserve the existing account/action. Do not create another primary conversion action.
5. Keep enhanced conversions off in the first publish unless the user-data source is rebuilt and validated.
6. Preview, submit one controlled Form 1 inquiry, and confirm one network request to the exact label.
7. Confirm delayed receipt in Google Ads before changing budgets or bidding.

Remediation update, 2026-07-09:

- GTM Version `23` added tag `275` for the existing action on trigger `260` only.
- GTM Version `24` added explicit `600 CAD` value continuity after no-send QA found GTM's omitted-value default was `0`.
- Tag `275` uses server `event_id` as Google transaction ID and keeps enhanced conversions disabled.
- Legacy tag `218` remains paused on its old trigger.
- Controlled production Form `1` event `c1a582b5-642e-4db3-bf95-0a5e925db784` reached the inquiry thank-you path and sent the exact action label, transaction ID, and `600 CAD` value. It carried no served-ad click ID, so campaign attribution is neither expected nor claimed.

### Deferred finding. Consent collection and tag gating are not implemented visibly

No common CMP, Google Consent Mode V2 command, or consent-state marker was found in sampled parent, Canada, or USA HTML. Every authenticated franchise GTM tag reports consent status `notSet`.

This is a privacy and measurement-governance gap, not a conclusion about legal compliance. CEFA should obtain privacy/legal approval for the final policy and deploy a CMP with explicit tag behavior for:

- `analytics_storage`;
- `ad_storage`;
- `ad_user_data`;
- `ad_personalization`.

This finding remains recorded for future governance work, but consent/CMP implementation is explicitly outside the current remediation blueprint by owner decision.

### Resolved audit interpretation. USA Meta browser `Lead` volume was misread from an unfiltered stats aggregation

For the seven-day dataset-stat window ending 2026-07-09:

- USA server `Lead` events: 5;
- USA browser `Lead` events: 680;
- the browser side contains bursts of 78, 199, and 399 events in single hourly buckets;
- GA4 reports one USA `generate_lead` on 2026-07-09, matching the controlled form submission rather than the 399-event browser burst;
- the in-house custom conversion last-fired timestamp still corresponds to the one approved test.

Follow-up investigation on 2026-07-09 proved that these values come from the unfiltered Pixel stats `aggregation=event` response and must not be interpreted as event-filtered Lead truth.

The correctly filtered and fully paginated query:

```text
aggregation=event_source&event=Lead
```

returned `7` browser and `6` server Lead events for 2026-07-01 through 2026-07-09: six normal browser/server pairs and one browser-only event. No live Meta tag was disabled. Future audits must use explicit `event=Lead` filtering and form/CRM business truth.

### Decision. A partner marker is optional, not required for the current comparison

- The two in-house ad sets use the marker-filtered in-house custom conversion.
- Active partner/Reshift USA ad set `120244631021560488` uses broad custom conversion `1915200622465036` / `USA Franchise Lead`.
- The broad conversion already requires Meta `Lead` on the USA inquiry thank-you path. Meta can attribute those results to the partner campaign/ad set without a separate partner marker.
- Partner conversion `1352507926817889` remains available but intentionally unused.

Current decision:

1. Keep the in-house marker and in-house custom conversion unchanged.
2. Keep the partner ad set on `USA Franchise Lead` and report it by campaign/ad-set ID.
3. Add a clearing-only rule so an exactly recognized partner campaign landing expires stale `fr_us_in_house` state without setting `fr_us_partner`.
4. Use Meta Experiments/A-B testing or mutually exclusive audiences when possible so campaign overlap does not muddy attribution.
5. Do not add `cefa_agency_test=fr_us_partner` or switch the partner ad set unless CEFA later requires a partner-only custom-conversion row independent of campaign attribution.
6. Confirm Looker/Supermetrics can expose campaign ID/name and the broad conversion action before declaring the reporting contract complete.

Remediation update, 2026-07-09:

- GTM Version `25` changed only tag `272`.
- The in-house marker now expires after seven days, matching the active Meta click-through attribution window.
- Exact Reshift campaign `120244631021580488`, ad set `120244631021560488`, or slug `reshift_meta` clears stale in-house state without storing a partner marker.
- Candidate tests passed ten precedence/expiry cases, and live browser tests confirmed in-house persistence, partner clearing, and direct-return preservation.

### P1. Parent event IDs are present but not unique

There are 76 duplicate event-ID rows across 6,424 parent entries, about 1.18%. The browser writes an ID only when the field is empty, and the server accepts a valid posted ID without checking whether another saved entry already used it.

The identifier must be server-enforced at saved-entry grain. A browser submission-attempt ID may be retained separately, but every Gravity Forms entry needs a unique immutable `event_id`.

### P1. The new parent attribution model misclassifies internal navigation

The browser correctly recognizes an own-site referrer in `sourceFromReferrer`, but `inferAdvertisingChannel` falls back to the raw referrer host. As a result, internal `cefa.ca` navigation is recorded as `referral/direct/referral` in the touch history.

This is visible in the native GA4 export and will distort first/current/all-source summaries. Own-site and approved cross-domain hosts must be excluded before channel inference.

### P1. Rich parent attribution is not saved with the form

The parent script now builds current, first, first non-direct, last non-direct, and an eight-touch history in localStorage. Those fields are merged into the browser dataLayer event, but Gravity Forms and the collector still save only fields 35-46:

- last UTM values;
- five click IDs;
- first landing page;
- first referrer.

The browser can therefore show richer attribution than CRM, collector, or business truth. The canonical model must be saved server-side with the entry and passed to CRM.

### P1. Franchise attribution is still dependent on GAConnector and ambiguous fields

Franchise Forms 1 and 2 expose hidden fields 14-30. The live writer reads GAConnector cookies and fills these fields, but it does not own a durable attribution model and does not include:

- event ID as a form field;
- Meta `fbclid`, `fbc`, or `fbp`;
- Google `gbraid` or `wbraid`;
- Microsoft `msclkid`;
- agency/test marker;
- consent state;
- explicit first and last non-direct timestamps;
- campaign/ad set/ad IDs.

The warehouse loader also searches field labels for `first source` and `last source`; the actual contract uses `lc_*` and `fc_*`. That is why first and last source are zero on all checked Canada and USA franchise rows.

### P1. The plugin's browser runtime is not truly multi-form

PHP configuration exposes multiple forms, but the JavaScript selects one global `formId` from the primary form and builds all selectors and listeners from it. If the main plugin replaces the franchise WPCode bridge without a refactor, Form 2 will not be handled reliably.

Refactor browser behavior around a form-contract map keyed by form ID before consolidating franchise tracking into the plugin.

### P1. Franchise enhanced conversions are configured against obsolete selectors

Canada final Google Ads tags have enhanced conversions enabled, but their variables read old Elementor IDs such as `form-field-email`, `form-field-phone`, and `form-field-first_name`. Current live forms are Gravity Forms with IDs such as `input_1_*`, and final conversion tags fire on the thank-you page where the form fields are no longer in the DOM.

The base conversion can still fire, but enhanced user data is not reliable. Rebuild this as a consent-aware server-side enhanced-conversions-for-leads path using the saved entry, not DOM selectors on a redirect page.

### P1. GA4 key-event definitions include micro actions

From 2026-06-09 through 2026-07-08:

- Parent: 2,722 `generate_lead`, 4,684 `find_a_school_click`, 628 `email_click`, and 328 `phone_click` key events.
- Franchise Canada: 60 `generate_lead` and 5 `fr_email_click` key events.
- Franchise USA: 16 `generate_lead` key events.

Only confirmed business submit events should be key events by default. Keep clicks as ordinary diagnostic events. This avoids broad "website leads" reports that combine intent and completion.

Remediation update, 2026-07-09:

- Parent `inquiry_click`, `email_click`, `phone_click`, and `find_a_school_click` are no longer key events.
- Franchise Canada `fr_application_click`, `fr_phone_click`, and `fr_email_click` are no longer key events.
- Parent and Franchise Canada retain `generate_lead` plus GA4's non-deletable `purchase` key event.
- Franchise USA definitions remain unchanged pending lifecycle dependency review.
- Event collection was not disabled; the clicks remain available as ordinary GA4 events.

### P1. Warehouse reconciliation reports zero GA4 leads even though GA4 is live

`mart_cefa_growth_dashboard.dashboard_form4_event_reconciliation_daily_latest` reports zero GA4 `generate_lead` events throughout the checked period. Live GA4 Data API and native export both contain the events. The current reconciliation model is reading an empty or stale GA4 serving surface.

Fix the model to use `analytics_267558140.events_*` or a governed normalized GA4 event fact. Do not present the current zero as an analytics outage.

### P1. Form-to-CRM identity is not deterministic

GreenRope attribution is current through 2026-07-08 and retains source evidence, but its governed table has no website `event_id` or form entry ID. Franchise form rows also have zero CRM/SiteZeus IDs. CEFA therefore cannot deterministically connect one submitted form to later tour, enrollment, franchise qualification, or closed outcome.

Every delivery integration should carry `cefa_event_id` and `cefa_form_entry_id` into an approved CRM custom field, and the CRM lead/opportunity ID should be written back to Gravity Forms entry meta when available.

### P2. Google UTM configuration uses two overlapping mechanisms

Both Google Ads accounts have an account tracking template:

`{lpurl}?utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_content={creative}&utm_term={keyword}`

In addition, 56 of 108 active parent Search ads and 7 of 11 active franchise Search ads have their own final URL suffix containing the same UTM keys. This can generate duplicate parameter names and two campaign-value conventions: numeric campaign ID and manual slug.

Move to one final URL suffix contract after click-preview validation. Preserve durable platform IDs and use the warehouse to look up names.

### P2. One-time public payload consumption is fragile

The WordPress REST payload routes are public and delete the transient on first read. A prefetch, scanner, duplicate browser request, or race can consume the payload before the intended browser event.

Use a short-lived signed payload that can be read idempotently, then rely on destination `event_id` / transaction-ID deduplication. If one-time semantics remain, add an explicit acknowledgement step rather than consuming on GET.

### P2. Collector delivery has no retry or audit ledger

The WordPress sender uses a two-second, nonblocking `wp_remote_post` and ignores the result. The Cloud Run receiver is signed and allowlisted, but WordPress has no queue, retry, dead-letter record, or delivery status.

Observed delivery is currently strong. Add Action Scheduler or Cloud Tasks with bounded retries and a no-PII delivery ledger before expanding the collector to all forms.

### P2. URL privacy filtering is too permissive

The attribution script removes only a short list of possible PII parameters and otherwise stores the full URL. Use a strict allowlist for approved attribution parameters and store host/path separately from approved query values. Click IDs are pseudonymous identifiers and should not be described as anonymous or no-identifier data.

### P2. Source classification and storage need hardening

- Source matching uses substring checks rather than exact host or registrable-domain rules.
- The cookie domain is derived from the full hostname, not a public-suffix-aware registrable domain.
- Multi-touch localStorage has no expiry even though attribution cookies use 90 days.
- A direct touch is recorded on each page and can fill history with internal navigation.
- Storage keys contain parent/Form 4 terminology even when the code is intended for other forms.

### P2. Meta and Google conversion inventories contain legacy clutter

- Parent Meta has 23 unarchived custom conversions, many stale since 2024-2025.
- Shared parent/Canada dataset mixes two business contexts.
- Google Ads accounts contain old Universal Analytics imports, click actions, app downloads, YouTube engagement, and legacy franchise actions.
- Two active parent Search campaigns still inherit customer-level Google goals; the rest of the current lead campaigns use safer campaign-level overrides.

Archive only after dependency and change-history review. The current three regional PMax campaigns are already isolated correctly and should not be changed merely because account-level goals are noisy.

Remediation update, 2026-07-09:

- Parent Search campaigns `14995905347` and `23854771600` now have explicit campaign-level goal overrides with only `SUBMIT_LEAD_FORM / WEBSITE` biddable.
- The Google Ads API accepted all 12 operations in `validateOnly=true` before apply.
- Read-back confirmed both Search campaigns and all three regional PMax campaigns have only the confirmed website form-submit goal biddable.
- No budgets, bidding strategies, ads, keywords, targeting, URLs, or campaign statuses changed.

### P2. Automated tests are missing

GitHub CI runs syntax and coding-standard checks only. There are no unit tests for attribution classification, ID rotation, payload replay, multi-form behavior, consent states, or field mappings.

### P2. Production state is ahead of GitHub

- Live parent JavaScript `0.4.5` matches the current local modified file, but `origin/main` remains at commit `7f06c03` and does not contain the complete current production state.
- Live USA GTM is Version 22, while several canonical docs still describe Version 18 or 19.
- The authorized service account can read the franchise GTM account but currently cannot list/read the parent GTM account.

Before new runtime work, create a reviewed production-state commit and export the three live GTM versions into a non-secret manifest or evidence pack.

## CEFA Attribution Bridge V1

### Design principles

1. Gravity Forms and CRM are business truth; browser/platform counts are destination evidence.
2. Website events stay neutral; destination naming remains in GTM/server adapters.
3. A server-confirmed `event_id` is the identity shared by browser, server, warehouse, and CRM.
4. Attribution uses first touch, current touch, and last non-direct touch. Direct traffic never erases a known non-direct source.
5. Parent, Franchise Canada, and Franchise USA remain separate attribution namespaces.
6. Capture only approved acquisition data. Do not put names, email, phone, addresses, or free text in dataLayer, URLs, logs, or unrestricted warehouse tables.
7. IDs are durable truth; names are descriptive attributes resolved from governed lookup tables.

### Recommended capture architecture

#### Server request capture

Add a host-scoped WordPress attribution service that runs on the landing request before GTM:

1. Parse only approved query parameters.
2. Classify the source with exact domain/suffix rules.
3. Ignore own-site referrers before channel inference.
4. Update a compact first-party attribution envelope containing first touch, last non-direct touch, current paid click IDs, and expiry.
5. Sign the envelope with a server HMAC so pre-submission code can reject tampering.
6. Keep each envelope below the cookie size limit and store no raw PII.

This captures acquisition even when GTM is late or blocked. Browser JavaScript remains useful for Gravity Forms rendering, `_ga`, `_fbp`, `_fbc`, session IDs, and bounded touch history.

#### Browser form writer

Use one form contract per form ID. For every supported form:

- fill only empty tracking fields;
- never overwrite School Manager, routing, or business fields;
- refresh after Gravity Forms render/AJAX events;
- refresh immediately before submit;
- apply explicit in-house marker precedence: current URL, current campaign-ID fallback, valid signed cookie, then blank;
- clear expired experiment markers;
- do not infer in-house ownership from a broad USA location alone.

#### Server pre-submission

On `gform_pre_submission_{form_id}`:

1. Verify and parse the signed attribution envelope.
2. Sanitize all values against length and character contracts.
3. Fill missing hidden fields from the verified server copy.
4. Prefer a click ID on the current request over an older stored click ID.
5. Generate or enforce a unique server event ID.
6. Save a separate browser `submission_attempt_id` when useful for diagnostics.

#### Saved-entry contract

Save normalized fields plus one bounded canonical JSON object in Gravity Forms entry meta. Suggested semantic fields:

| Family | Fields |
|---|---|
| Contract | `attr_schema_version`, `attr_captured_at`, `attr_expires_at` |
| Identity | `event_id`, `submission_attempt_id`, `form_id`, `form_family`, `site_context`, `business_unit`, `market`, `country` |
| First touch | `first_source`, `first_medium`, `first_campaign`, `first_campaign_id`, `first_content`, `first_term`, `first_landing_host`, `first_landing_path`, `first_referrer_host`, `first_referrer_path`, `first_touch_at` |
| Last non-direct | `last_source`, `last_medium`, `last_campaign`, `last_campaign_id`, `last_content`, `last_term`, `last_landing_host`, `last_landing_path`, `last_touch_at` |
| Click IDs | `gclid`, `gbraid`, `wbraid`, `fbclid`, `msclkid`, `fbc`, `fbp` |
| Platform IDs | `google_campaign_id`, `google_ad_group_id`, `google_ad_id`, `meta_campaign_id`, `meta_adset_id`, `meta_ad_id` |
| Experiment | `test_id`, `agency_test`, `agency_resolution_source` |
| Analytics | `ga_client_id`, `ga_session_id` |
| History | `touch_count`, bounded `touch_history_json` in entry meta only |

Do not assign new Gravity Forms numeric IDs from this document. Export each live form schema, add fields in a controlled form revision, then record the approved IDs in `class-cefa-conversion-tracking-config.php` and a versioned field-map file.

#### CRM handoff

Create approved CRM fields for:

- `cefa_event_id`;
- `cefa_form_entry_id`;
- first source/medium/campaign/campaign ID;
- last non-direct source/medium/campaign/campaign ID;
- click IDs in restricted fields;
- agency/test ID;
- source landing/referrer host/path.

Pass them in the existing KinderTales/GreenRope and Synuma/SiteZeus delivery payloads. When the destination returns a lead/opportunity ID, write it back to Gravity Forms entry meta. Public analytics marts should retain booleans/hashes; a restricted warehouse table may hold encrypted identifiers required for approved offline conversion uploads.

### UTM contract

Use IDs as stable keys and names/slugs as optional context.

#### Meta

Recommended URL Tags baseline:

```text
utm_source={{site_source_name}}&utm_medium=paid_social&utm_campaign=<governed_campaign_slug>&utm_id={{campaign.id}}&utm_adset={{adset.id}}&utm_ad={{ad.id}}&utm_content={{ad.name}}&utm_term={{adset.name}}
```

The current in-house test adds exactly one explicit field:

```text
cefa_agency_test=fr_us_in_house
```

The current partner campaign does not require a partner marker because it uses the existing broad USA inquiry custom conversion and is separated in reporting by campaign/ad-set ID.

#### Google Ads

Use one final URL suffix mechanism, not both a tracking template and duplicate ad suffixes. Proposed baseline after click-preview validation:

```text
utm_source=google&utm_medium=cpc&utm_id={campaignid}&utm_campaign={campaignid}&utm_content={adgroupid}-{creative}&utm_term={keyword}&utm_matchtype={matchtype}&utm_device={device}&utm_network={network}
```

Campaign/ad-group names should be joined from API snapshots by ID. Keep auto-tagging enabled so Google can preserve `gclid`, `gbraid`, or `wbraid`.

### Destination adapters

#### GA4

- Map all final neutral submits to `generate_lead` with form/business metadata.
- Keep clicks and form interactions as ordinary events, not key events.
- Register only low-cardinality custom dimensions needed in the UI.
- Keep `event_id`, platform IDs, and detailed touch fields in BigQuery even when they are not GA4 UI dimensions.
- Do not use GA4 as the primary form count.

#### Google Ads

- One primary final-submit action per campaign objective.
- Pass server `event_id` as transaction ID for browser tag deduplication.
- Keep GA4 imports secondary if a direct Ads tag is the primary action.
- Implement enhanced conversions for leads from the saved server entry after a separately approved user-data policy, not stale DOM selectors.
- Upload qualified lifecycle conversions as secondary first. Promote only after CRM reconciliation and value approval.

#### Meta

- Browser and CAPI use the same standard event and the same `event_id`.
- Preserve browser/server event-ID dedup and currently approved match keys in CAPI.
- Keep inquiry and submit-a-site distinguishable with custom parameters and separate custom conversions.
- Keep the in-house agency marker as an event parameter and custom-conversion rule, not a new fake event name.
- Investigate raw event pollution before relying on broad `Lead` volume.

#### Collector and warehouse

- Expand the collector from parent Form 4 to all approved forms after a versioned schema is ready.
- Queue and retry delivery; log no-PII status by `event_id`.
- Normalize GA4 native export into a current event fact.
- Add `form_id`, `form_family`, `event_id`, platform IDs, first/last touch, and experiment marker to franchise raw/fact contracts.
- Replace label-regex field discovery with explicit versioned field-ID maps.
- Reconcile saved form, collector, GA4, Google Ads, Meta, and CRM by event ID where the destination supports it.

## Execution Plan

### Phase 0: Freeze and baseline

Estimated effort: 1-2 working days.

1. Commit the reviewed plugin `0.4.5` production state separately from unrelated warehouse work.
2. Export live GTM Versions parent/current, Canada 54, and USA 22 into a redacted evidence pack.
3. Restore read access for the GTM service account to parent account `4591216764`.
4. Export all five live Gravity Forms schemas and current delivery-feed mappings.
5. Snapshot GA4 key events, Google conversion goals/actions, Meta custom conversions, active ad-set promoted objects, and active URL tags.
6. Freeze new conversion actions and tag sources until Phase 1 is signed off.

Exit gate: GitHub and evidence packs reproduce the live production state.

### Phase 1: Repair immediate destination gaps

Estimated effort: 2-5 working days plus platform processing time.

1. Restore one USA Google Ads final-submit tag on the existing action and helper dispatch.
2. Add transaction ID and verify one controlled conversion.
3. Investigate the USA Meta browser `Lead` bursts in Events Manager.
4. Confirm partner reporting uses campaign/ad-set ID plus the existing broad USA inquiry conversion; do not add a partner marker in the current scope.
5. Remove key-event status from GA4 micro actions after impact review.
6. Move the two customer-goal-level parent Google campaigns to explicit final-lead campaign goals if they are intended as lead campaigns.
7. Standardize Google UTM mechanics in a validate/preview rollout.

Exit gate: one real form submit per live form reaches only the approved final destinations once; the in-house marker does not appear on non-in-house traffic; partner results are reportable by campaign/ad-set ID.

### Phase 2: Build Attribution Bridge V1

Estimated effort: 1-2 development weeks.

1. Refactor JavaScript to use multiple form contracts rather than one global `formId`.
2. Fix own-site referrer handling, exact source classification, expiry, and strict URL allowlisting.
3. Implement server request capture and signed attribution envelope.
4. Implement unique server event IDs and separate browser attempt IDs.
5. Add explicit form field maps and canonical entry-meta JSON.
6. Add unit tests for classification, precedence, expiry, in-house marker conflicts, PII stripping, duplicate IDs, and multi-form handling.
7. Add integration tests for REST payload replay and collector retries.

Exit gate: automated tests pass and no production form/business field is overwritten.

### Phase 3: Shadow migration beside GAConnector

Estimated observation window: 2-4 weeks.

1. Add new canonical hidden fields without removing fields 14-30 or 35-46.
2. Populate both old and new contracts, but let existing fields remain operational truth.
3. Compare per-entry parity for source, medium, campaign, landing/referrer, click IDs, and client ID.
4. Investigate every mismatch category and publish a daily parity report.
5. Verify Safari/iOS, Chrome, Firefox, direct, paid, organic, referral, GBP, AI referral, email, and in-house-test journeys.
6. Keep all bidding and CRM routing unchanged during the shadow period.

Exit gate: at least 98% paid-entry parity, 100% unique event IDs, no in-house false positives, and no business-delivery regression.

### Phase 4: CRM identity and lifecycle outcomes

Estimated effort: 1-2 weeks, dependent on CRM owners.

1. Add `cefa_event_id` and approved attribution fields to GreenRope/KinderTales and Synuma/SiteZeus mappings.
2. Write destination lead/opportunity IDs back to Gravity Forms entry meta.
3. Add restricted identifier tables and public redacted facts in BigQuery.
4. Build deterministic form-to-CRM lifecycle views.
5. Define qualified lead, tour, enrollment, franchise qualification, and closed outcome rules.

Exit gate: a sampled form can be followed by `event_id` into CRM and back into the governed warehouse without exposing PII in public marts.

### Phase 5: Server-side destination hardening

Estimated effort: 1-2 weeks plus learning windows.

1. Replace obsolete GTM enhanced-conversion selectors with saved-entry server uploads after the user-data implementation receives separate approval.
2. Standardize Meta CAPI browser/server dedup and match keys.
3. Launch Google and Meta lifecycle events as secondary/reporting signals.
4. Reconcile at least two full attribution windows before promoting any lifecycle event to primary bidding.
5. Add replay/dead-letter controls and destination receipt logging.

Exit gate: browser, server, platform, and CRM counts reconcile within approved tolerances.

### Phase 6: Remove legacy dependencies

1. Make the CEFA bridge primary only after shadow acceptance.
2. Keep GAConnector fallback for one rollback window.
3. Remove GAConnector scripts and the franchise WPCode bridge one property at a time.
4. Archive stale GTM tags and custom conversions only after dependency review.
5. Keep redacted exports and rollback instructions.

Exit gate: no live form depends on GAConnector/WPCode for attribution or confirmed-submit delivery.

## Test Matrix

Every release must cover:

| Dimension | Cases |
|---|---|
| Forms | Parent 4; Canada 1/2; USA 1/2 |
| Acquisition | Direct; UTM-only; `gclid`; `gbraid`; `wbraid`; Meta UTM + `fbclid`; GBP; organic search; AI referral; email; in-house marker; partner campaign without marker |
| Form behavior | first render; AJAX re-render; validation failure; successful submit; double click; back/reload; token prefetch/retry |
| Browser | Chrome desktop/mobile; Safari/iOS; Firefox |
| Destinations | saved entry; collector; dataLayer; GA4; Google Ads; Meta browser/CAPI; CRM; BigQuery |

For each successful submit, assert:

1. One saved entry and one unique event ID.
2. Correct form family, market, and business unit.
3. Correct first and last non-direct attribution.
4. Correct click-ID and in-house-marker precedence.
5. No PII in dataLayer, URL logs, or unrestricted warehouse rows.
6. One approved final destination event, with browser/server dedup where applicable.
7. CRM contains the same event ID and approved attribution fields.

## Operational SLOs

| Measure | Target |
|---|---:|
| Saved entries with valid unique event ID | 100% |
| Saved paid entries with UTM or click-ID evidence | >= 98% |
| Collector distinct event-ID coverage after retry window | >= 99.9% |
| Internal referrals in acquisition history | 0 |
| In-house marker false positives outside the in-house campaign | 0 |
| Final event duplicate rate by event ID | 0 |
| CRM rows with website event ID after cutover | >= 99% |
| PII findings in unrestricted event/attribution tables | 0 |

## Do Not Do

- Do not create a new event name per agency, campaign, or location.
- Do not add a partner marker or switch the partner conversion unless CEFA later requires partner-only custom-conversion reporting independent of campaign attribution.
- Do not optimize lead campaigns to clicks, email clicks, directions, video views, or broad website-lead bundles.
- Do not remove GAConnector before a measured shadow period.
- Do not put email, phone, names, addresses, or free text in dataLayer.
- Do not rely only on a thank-you URL or a UTM present at the final page.
- Do not upload offline conversions until event identity and CRM stage definitions are stable.
- Do not change campaign goals and tracking implementation simultaneously without a baseline and rollback.

## Recommended Decision

Approve the following order:

1. Repair USA Google Ads final-submit receipt.
2. Investigate USA Meta raw `Lead` pollution.
3. Keep the current partner broad conversion and validate campaign-level reporting.
4. Build and shadow CEFA Attribution Bridge V1.
5. Carry `event_id` through CRM and lifecycle outcomes.
6. Add server-side enhanced/offline conversion signals only after reconciliation and separate user-data approval.

This preserves the conversions that currently work while fixing the identity and attribution foundation underneath them.

## Source Evidence

- Live website and public GTM runtime checks on 2026-07-09.
- Authenticated GTM read for Franchise Canada Version 54 and Franchise USA Version 22.
- GA4 Admin/Data API and native BigQuery export checks through 2026-07-08.
- Google Ads API v24 read-only queries for customers `4159217891` and `3820636025`. See [Google Ads API release notes](https://developers.google.com/google-ads/api/docs/release-notes).
- Meta Ads MCP and read-only Graph API checks for parent and franchise accounts, datasets, custom conversions, active ad sets, and active ads.
- BigQuery checks of Gravity Forms, collector, GreenRope, franchise forms, and dashboard reconciliation surfaces.
- Runtime source in `assets/js/`, `includes/`, `snippets/`, and `collector/` in this repo.
