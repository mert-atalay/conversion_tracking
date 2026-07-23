# CEFA Measurement And Activation Program Register

**Register date:** 2026-07-23
**Owner:** CEFA marketing measurement
**Status vocabulary:** `Verified`, `Active guarded`, `Approved`, `Pending`,
`Blocked`, and `Reference only`

## Purpose

This is the operational control page for CEFA conversion tracking, attribution,
marketing data engineering, and platform activation. It records:

- what is live now;
- what CEFA has approved;
- what is still being built;
- what is waiting on an external dependency or decision;
- which system owns each responsibility;
- which acceptance gates must pass before production cutover.

Detailed implementation documents remain authoritative for their own
workstreams. This register is the cross-workstream status and sequencing
authority. Update it when a major dependency, deployment state, vendor scope,
or production gate changes.

## Non-Negotiable Boundaries

1. Parent inquiry truth starts with Gravity Forms Form `4`.
2. CEFA School Manager continues to own Form `4` business delivery to
   KinderTales. Tracking work must not change its program, school, day, or CRM
   delivery behavior.
3. GreenRope is the approved parent CRM lifecycle source for the current
   offline-conversion project. It does not replace KinderTales.
4. Franchise Canada and Franchise USA remain separate from the parent path.
   Their existing GAConnector and Synuma/SiteZeus production flow stays in
   place until a documented cutover passes.
5. Website inquiry/application conversions remain primary. New CRM-stage
   conversions launch as secondary reporting signals and are not used for
   bidding without a later explicit decision.
6. The same `cefa_event_id` must be preserved across browser, server, form,
   CRM, warehouse, Google, and Meta paths where the event is the same.
7. Browser and server copies of one event must deduplicate. No tool may create
   a second business conversion merely because it has a different transport.
8. No raw parent or child PII belongs in marketing BigQuery tables, logs, or
   diagnostics. Restricted identity processing follows the approved HMAC and
   transient hashing contracts.
9. Existing dashboard contracts do not change until reconciliation passes and
   the replacement is explicitly promoted.

## Executive Status

| Workstream | State | Current reality | Next gate |
|---|---|---|---|
| Parent website attribution | `Verified` | CEFA Conversion Tracking `0.6.3` and the canonical Form `4` writeback improve fields `35-46`; School Manager and KinderTales remain unchanged | Continue production monitoring |
| Parent website conversions | `Verified` | `school_inquiry_submit` continues to feed the existing GA4, Google Ads, and Meta inquiry destinations | Preserve once-only firing during sGTM work |
| Franchise attribution replacement | `Active guarded` | CEFA attribution and ledger run in shadow beside GAConnector on Canada Forms `1/2` and USA Forms `1/2`; no legacy field or Synuma payload cutover | Complete evidence window, resolve delivery alerts, approve field mapping and rollback |
| Parent CRM offline conversions | `Active guarded` | Restricted BigQuery, capture, binder, poller, dispatcher, diagnostics, three Google actions, and three Meta test events are built; production sending is disabled | GreenRope fields, controlled identity test, eligibility decision, production activation |
| Google CRM-stage destinations | `Verified` | Three secondary, non-biddable actions exist and all passed Data Manager `validateOnly=true` | First eligible prospective CRM outcome |
| Meta CRM-stage destinations | `Active guarded` | All three custom server events passed Meta Test Events | First legitimate live event must enter Meta's registry before reporting custom conversions can be created |
| BigQuery and Google Cloud foundation | `Active guarded` | BigQuery, Cloud Run, Scheduler, Secret Manager, restricted activation storage, source loaders, and monitoring patterns exist | Productionize Dataform, reconciliation assertions, alerts, queues, and runbooks |
| Dataform | `Active guarded` | Additive QA foundation exists; Cloud Run remains the production orchestrator | Parallel compile/assertion proof, then incremental promotion |
| Stape Business sGTM | `Approved` | CEFA approved Business tier as the managed server-side tagging layer; no production container or routing cutover is recorded yet | Provision CEFA-owned account/container access, domain design, build and shadow QA |

## Immediate Waiting List

| Dependency | Owner | Why it is required | What happens after it is complete |
|---|---|---|---|
| GreenRope opportunity field `cefa_event_id` | GreenRope account owner/admin or vendor | Stores the exact Form `4` event identity on the opportunity | Binder write/read-back test |
| GreenRope opportunity field `cefa_form_entry_id` | GreenRope account owner/admin or vendor | Confirms the matched Gravity Forms entry | Controlled end-to-end identity test |
| Controlled parent inquiry | CEFA measurement owner | Proves Gravity Forms, GreenRope, KinderTales, and existing conversions agree | Enable eligible prospective lifecycle processing |
| Per-record platform eligibility decision | CEFA | Runtime currently fails closed when eligibility is unknown | Enable platform dispatch only for approved records |
| Meta live custom-event registration | Meta, triggered by first legitimate eligible outcome | Test Events do not currently expose the event type to reporting custom-conversion creation | Create three reporting-only custom conversions |
| Stape Business workspace and administrative access | CEFA/vendor | Required to create and own server containers, logs, domains, and rollback | Begin sGTM build in non-disruptive shadow mode |
| DNS path for first-party tagging endpoints | CEFA website/DNS owner | Required for first-party server-side collection | Validate endpoint, cookies, routing, and rollback |
| Cloud/data delivery statement of work | CEFA/vendor | Prevents rebuilding existing infrastructure or creating an isolated warehouse | Start bounded Dataform/Cloud hardening work |
| Franchise shadow evidence and Synuma review | CEFA measurement owner | GAConnector must not be replaced on sparse or delivery-uncertain evidence | Approve, extend, or reject franchise cutover |

## Approved Tooling And Commercial Register

The values below record the decision evidence supplied to the project. Finance
or procurement remains authoritative for invoices, taxes, term dates, and
renewals.

| Item | Approved reference | Intended use | Registration status |
|---|---:|---|---|
| BigQuery + Dataform + Cloud Run/Scheduler + Pub/Sub/Cloud Tasks + Secret Manager development | `$3,377` quoted line | Complete and harden CEFA's existing marketing data and intelligence foundation | Approved scope; statement of work and delivery ownership still need confirmation |
| Stape Business | `$83/month`, billed `$1,000/year`, up to `5M` requests in supplied plan image | Managed sGTM hosting, multi-domain capability, 10-day logs, monitoring, first-party routing and server-side destination delivery | Approved tier; provisioning and implementation pending |
| Separate server-side GTM quoted line | `$1,370` quoted line | Implementation and/or managed service associated with Stape/sGTM | Commercial contents must be reconciled with the `$1,000/year` Stape license to prevent duplicate billing |

The approved Stape Business features are capabilities, not automatic
production permissions. Custom Loader, Cookie Keeper, Enricher, File Proxy,
request delay, scheduled requests, and IP blocking must each be enabled only
when they serve an approved tracking requirement and pass QA.

## Target Architecture

```text
Parent website
  -> CEFA Conversion Tracking + web GTM
  -> Gravity Forms Form 4
       -> School Manager -> KinderTales
       -> exact identity -> GreenRope
  -> first-party Stape sGTM endpoint
       -> GA4
       -> Google Ads website conversions
       -> Meta Pixel/CAPI with event_id deduplication

GreenRope prospective lifecycle
  -> Cloud Run poller/webhook
  -> restricted BigQuery lifecycle ledger and outbox
  -> Google secondary CRM-stage conversions
  -> Meta CRM-stage server events

Franchise Canada and USA
  -> existing website/GTM/GAConnector/Synuma production flow
  -> CEFA canonical attribution shadow
  -> later first-party sGTM path with property and destination isolation

All approved source facts
  -> BigQuery
  -> Dataform transformations and assertions
  -> certified reporting, intelligence, and activation contracts
```

## Stape Business Implementation Contract

### Required design

- CEFA owns the Stape account, billing relationship, GTM server containers,
  templates, custom domains, and administrative access.
- Use first-party endpoints. Proposed names must be checked against existing
  DNS before creation; examples are `metrics.cefa.ca` and equivalent
  first-party endpoints for each franchise property.
- Parent, Franchise Canada, and Franchise USA must remain isolated by
  hostname, event taxonomy, GA4 property, Google destination, Meta dataset,
  form identity, and debug evidence. One Stape account may manage them, but
  traffic cannot cross destinations.
- Keep the web GTM layer for browser interaction capture. sGTM is an additive
  processing and delivery layer, not a blind replacement.
- Forward the existing neutral event names. Do not invent parallel events to
  distinguish browser and server transport.
- Preserve the same `cefa_event_id` as Google transaction/dedup identity and
  Meta `event_id` when browser and server represent the same conversion.
- Keep parent School Manager/KinderTales and franchise Synuma/SiteZeus outside
  the sGTM critical path.
- Carry consent/eligibility state through the request. Server-side transport
  must not convert an ineligible event into an eligible event.
- Use approved user-data fields only. Hashing, redaction, logging, retention,
  and destination rules must be documented before enhanced matching is
  enabled.

### Rollout sequence

1. Inventory current web GTM tags, destination IDs, event IDs, consent inputs,
   custom scripts, WordPress attribution, and existing CAPI behavior.
2. Provision Stape Business under CEFA ownership and export a baseline
   configuration.
3. Configure first-party test endpoints and server containers without
   changing production destinations.
4. Route page and non-conversion events in debug/shadow mode.
5. Add GA4 server routing and reconcile client/server sessions and event
   parameters.
6. Add Google Ads and Meta conversion routes using the existing neutral
   events and exact deduplication IDs.
7. Run controlled Form `4`, Franchise Canada Form `1`, and Franchise USA Form
   `1` tests. Do not create business leads merely for infrastructure QA unless
   the test can be clearly excluded.
8. Compare browser-only, server-received, destination-received, form, CRM, and
   warehouse totals.
9. Promote one property at a time with a documented rollback.
10. Remove a browser destination tag only if its server replacement is proven
    and deduplicated. Do not remove the browser event/data layer itself.

### Acceptance gates

- First-party endpoint and DNS/TLS health pass.
- No parent/franchise hostname or destination cross-talk.
- Existing website conversion fires once.
- Browser/server duplicate conversions equal zero.
- Event ID is present and stable across all copies of one event.
- Required school, form, campaign, source, click-ID, landing-page, and
  referrer fields reconcile to the form and canonical attribution record.
- Meta Pixel/CAPI deduplication is confirmed in Events Manager.
- Google Ads website conversion diagnostics show the intended source and no
  duplicate action.
- GA4 event names and key parameters remain compatible with current reports.
- No KinderTales or Synuma delivery regression.
- No prohibited PII appears in Stape logs, BigQuery, Cloud Logging, GTM debug
  exports, or documentation.
- Monitoring, access inventory, configuration export, change log, cost alert,
  and rollback runbook exist.

## BigQuery And Google Cloud Development Contract

### Keep and extend

- Reuse project `marketing-api-488017`.
- Keep BigQuery as marketing measurement and intelligence truth.
- Keep Cloud Run for API extraction, webhooks, custom processing, offline
  activation, and backward-compatible refresh entrypoints.
- Move stable BigQuery SQL transformations into Dataform incrementally.
- Keep Secret Manager as the credential boundary.
- Use Cloud Scheduler for bounded schedules.
- Use Pub/Sub or Cloud Tasks only where asynchronous delivery, retries,
  fan-out, or dead-letter handling is required. Do not add both by default.
- Preserve existing dashboard-safe contracts until promoted replacements
  reconcile.

### Required deliverables

- Source and transformation inventory with owner, schedule, service account,
  destination, freshness expectation, retry policy, and cost class.
- Dataform repository/release/workflow configuration tied to Git.
- Assertions for freshness, uniqueness, row counts, null safety, spend
  reconciliation, lead reconciliation, stage deduplication, and dashboard
  compatibility.
- Cloud Monitoring alerts for failed jobs, stale sources, failed assertions,
  delivery failures, and budget/query guardrails.
- Idempotent queues and dead-letter visibility for webhook or activation work
  that requires retries.
- Least-privilege IAM and secret-level access.
- Artifact-to-commit traceability, deployment runbooks, rollback procedures,
  and a CEFA-owned handoff.
- Bounded retention and partitioning, especially for click IDs and restricted
  activation data.
- No duplicate warehouse, disconnected Google Cloud project, parallel school
  registry, or vendor-only source repository.

### Promotion gates

- Dataform compiles and all critical assertions pass in parallel.
- Source totals reconcile with the existing production pipeline.
- Dashboard outputs remain unchanged unless an approved contract changes.
- Cloud costs and request volume remain within approved guardrails.
- Runtime identities can access only their required datasets, jobs, queues,
  and secrets.
- Every production service has monitoring, failure ownership, and rollback.

## Sequenced Build Board

| Order | Work package | Current state | Exit condition |
|---:|---|---|---|
| 1 | Preserve current website and CRM delivery paths | `Verified` | Continuous |
| 2 | Create GreenRope identity fields | `Pending` | Both fields visible through API |
| 3 | Parent controlled identity test | `Blocked` by item 2 | Exact Form `4`/GreenRope match; KinderTales succeeds; existing conversions fire once |
| 4 | Parent CRM offline production activation | `Blocked` by items 2-3 and eligibility | Eligible prospective outcomes accepted; baseline uploads and duplicates remain zero |
| 5 | Stape Business provisioning and architecture inventory | `Approved` | CEFA ownership, access, domains, routing map, baseline export |
| 6 | Stape shadow implementation | `Pending` | Browser/server parity and no destination cross-talk |
| 7 | Stape conversion promotion by property | `Pending` | Once-only conversions, deduplication and CRM continuity pass |
| 8 | Dataform productionization | `Active guarded` | Stable transforms and assertions proven in parallel |
| 9 | Cloud monitoring, queue and runbook hardening | `Pending` | Alerts, retries, dead letters, cost controls and rollback pass |
| 10 | Franchise GAConnector decision | `Active guarded` | Evidence and Synuma gates determine cutover or continued coexistence |

## Change Control

Update this register when:

- a waiting item is completed or newly blocked;
- a platform destination is created, promoted, paused, or selected for
  optimization;
- a Stape domain, container, power-up, or production route changes;
- a Cloud Run, Dataform, Scheduler, Pub/Sub, Cloud Tasks, Secret Manager, or
  BigQuery production contract changes;
- a parent, franchise, KinderTales, GreenRope, GAConnector, or Synuma ownership
  boundary changes;
- a commercial term or delivery scope is confirmed.

Never put passwords, tokens, cookie values, raw identifiers, parent/child PII,
or private payloads in this register.

## Authoritative Detail

- [BigQuery marketing intelligence blueprint](../superpowers/plans/2026-06-12-bq-marketing-intelligence-blueprint.md)
- [Parent CRM offline-conversion blueprint](../superpowers/plans/2026-07-23-parent-crm-offline-conversion-activation-blueprint.md)
- [Parent CRM offline-conversion implementation report](../10-conversion-tracking/parent-crm-offline-conversion-implementation-report.md)
- [Parent Form 4 and KinderTales boundary](../10-conversion-tracking/parent-form4-kindertales-attribution-boundary-2026-07-10.md)
- [Parent canonical writeback observation](../10-conversion-tracking/parent-paid-writeback-production-observation-2026-07-10.md)
- [Franchise GAConnector shadow rollout](../10-conversion-tracking/franchise-gaconnector-shadow-rollout-2026-07-20.md)
- [Full conversion-tracking assessment](../10-conversion-tracking/full-conversion-tracking-assessment-and-execution-plan-2026-07-09.md)
