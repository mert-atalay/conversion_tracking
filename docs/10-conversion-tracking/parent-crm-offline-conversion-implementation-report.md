# Parent CRM Offline Conversion Implementation Report

**Report date:** 2026-07-23
**Rollout:** CEFA parent CRM offline conversions
**Approved mode:** Immediate per-record production rollout after deterministic tests
**Current production state:** Infrastructure and non-uploadable baseline deployed;
production dispatch disabled on deterministic blockers
**Blueprint:** `docs/superpowers/plans/2026-07-23-parent-crm-offline-conversion-activation-blueprint.md`

## Executive Status

The restricted warehouse, GreenRope poller, Form 4 identity capture, identity
binder, outbox dispatcher, diagnostics runtime, and three Google reporting
actions are deployed. A successful
2026-07-23 baseline stored `22,328` unique current-state opportunities as
`baseline_non_uploadable`; it created zero lifecycle events, outbox rows, or
delivery attempts. A disabled-dispatcher execution also processed and sent
zero rows.

Production sending remains disabled. The live GreenRope opportunity schema
lacks the two exact identity fields required to connect a CRM outcome safely
to one Form 4 submission. CEFA's isolated prospective identity path is active:
it captures Form 4 entries every five minutes into a restricted HMAC-only
inbox, and the binder checks GreenRope every 15 minutes. GreenRope writes
remain disabled until its vendor creates the required fields and one
controlled write/read-back test passes. Google Data Manager validation has
passed for all three actions under the production service account. Meta Test
Events has accepted all three synthetic CRM event types under the production
runtime; Meta's custom-conversion endpoint still returns subcode `1760020`
until those event types enter its live event registry. Per-record
consent/eligibility remains fail-closed as `unknown`.

The approved rollout does not wait for aggregate identity coverage or a fixed
number of days. Once the exact identity handoff passes one controlled inquiry
and the Google/Meta tests pass, every eligible prospective record can be sent
immediately. Unsafe records remain quarantined individually.

## Current Safety State

```text
PARENT_ACTIVATION_MODE=disabled
GOOGLE_OFFLINE_UPLOAD_ENABLED=false
META_CRM_CAPI_ENABLED=false
GREENROPE_LIFECYCLE_WEBHOOK_ENABLED=false
```

The three Google reporting actions and their exclusive non-biddable customer
goals were created/configured. No campaign budget, bidding strategy, status,
campaign goal, WordPress form, School Manager flow, KinderTales delivery,
existing inquiry conversion, Meta campaign/ad set, or GreenRope field was
changed.

## Deployment Record

| Resource | 2026-07-23 deployed state |
|---|---|
| Activation container | `parent-crm-activation:20260723-full-rollout-v10` |
| Activation image digest | `sha256:87669f97ff05ba6646fe109aa489b5d549d4e7337812c215cc7010130ee6aa6c` |
| Form 4 capture job | `cefa-parent-form4-identity-capture` |
| Form 4 capture schedule | `cefa-parent-form4-identity-capture-5m`; every five minutes; enabled |
| Capture scheduler smoke test | Manual execution `cefa-parent-form4-identity-capture-swfwf` completed successfully; automatic execution created at `2026-07-23 21:05 UTC` |
| Identity binder job | `cefa-parent-greenrope-identity-binder` |
| Identity binder schedule | `cefa-parent-greenrope-identity-binder-15m`; minutes 2, 17, 32, and 47; enabled |
| Identity binder write mode | `PARENT_GREENROPE_IDENTITY_WRITE_ENABLED=false` |
| Binder scheduler smoke test | Scheduled execution `cefa-parent-greenrope-identity-binder-brpl2` completed successfully; two delayed candidates remained retryable; zero writes |
| Poller job | `cefa-parent-crm-lifecycle-refresh` |
| Poller schedule | `cefa-parent-crm-lifecycle-refresh-15m`; enabled; runtime mode remains disabled |
| Dispatcher job | `cefa-parent-offline-conversion-dispatch` |
| Dispatcher schedule | `cefa-parent-offline-conversion-dispatch-5m`; enabled; both platform send switches remain false |
| Diagnostics job | `cefa-parent-conversion-diagnostics` |
| Diagnostics schedule | `cefa-parent-conversion-diagnostics-30m`; enabled |
| Google validation job | `cefa-parent-google-data-manager-validate`; execution `cefa-parent-google-data-manager-validate-wqsxk` passed all three actions |
| Meta Test Events job | `cefa-parent-meta-test-events`; execution `cefa-parent-meta-test-events-ckkft` received all three synthetic events |
| Runtime identity | `marketing-cefa-795@marketing-api-488017.iam.gserviceaccount.com` |
| Restricted dataset | `marketing-api-488017.cefa_parent_activation_restricted` |
| Dataset access | Activation runtime `WRITER`; designated Codex/admin identities `OWNER`; no project-wide group access |
| Baseline execution | `cefa-parent-crm-lifecycle-refresh-hvh5p` |
| Baseline result | `baseline_established=true`; 39,087 source observations; 22,328 unique stored snapshots; zero group errors |
| Baseline activation result | Zero lifecycle events, outbox rows, and delivery attempts |
| Dispatcher safety execution | `cefa-parent-offline-conversion-dispatch-gfmdh` |
| Dispatcher safety result | Disabled mode; zero inspected, tested, validated, accepted, retried, or failed |

## Verified Live Evidence

| Area | Evidence | Result |
|---|---|---|
| Form identity | Form 4 field `32.4` is the CEFA event ID | Available |
| Form attribution | Form 4 fields `35-46` save UTMs, click IDs, landing page, and referrer | Available |
| Prospective Form capture | Form 4 entries after `2026-07-23 20:45:00 UTC` are HMAC-captured into the restricted inbox | Enabled every five minutes |
| Capture safety | Raw parent identity is normalized/HMACed in Cloud Run memory; no raw email, phone, name, child data, or payload is persisted | Passed schema and focused tests |
| Prospective live capture | Six Form 4 identities captured as of `2026-07-23 21:32 UTC`; zero raw PII stored | Active |
| Delayed CRM creation | A Form 4 entry without a GreenRope candidate remains `retryable_failure`, not permanently quarantined | Implemented |
| Identity binder | Deterministic same-school, same-email-HMAC, 24-hour matcher with unique-best safeguards | Enabled read-only; GreenRope writes disabled |
| Historical matcher audit | 490 of 500 recent Form 4 entries resolved deterministically; 10 remained safely unmatched | 98% resolution; audit only |
| Form handoff | Feed `4` is `CEFA Dashboard Parent Inquiry Handoff` to `cefa-brain.vercel.app` | Existing |
| KinderTales | School Manager independently performs KinderTales business delivery | Existing and out of activation path |
| WordPress GreenRope writer | Live plugin review found no GreenRope writer in CEFA Conversion Tracking or School Manager | Not found |
| GreenRope event identity | Live field dictionary lacks `cefa_event_id` | Blocked |
| GreenRope entry identity | Live field dictionary lacks `cefa_form_entry_id` | Blocked |
| GreenRope history | Existing API extraction represents current state | Initial baseline stored; prospective polling remains disabled |
| GreenRope scope | 52 approved parent-school groups; `TEST - Systems` excluded | Enforced by poller allowlist |
| Restricted warehouse | `marketing-api-488017.cefa_parent_activation_restricted` | Deployed with narrowed dataset IAM |
| Initial baseline | 22,328 unique snapshots in one poll run | 100% `baseline_non_uploadable`; zero activation rows |
| Cloud Run runtime | Capture, binder, poller, dispatcher, and diagnostics jobs on activation v10 | Deployed; GreenRope/platform send switches disabled |
| Google CRM actions | Actions `7695582127`, `7695186674`, and `7695186677` | Created, secondary, non-biddable, no campaign/custom-goal inclusion |
| Google Data Manager API | Enabled in project `marketing-api-488017` | Three `validateOnly=true` requests passed under the runtime service account |
| Meta CRM Test Events | Three approved custom event types | Three received, zero API messages, synthetic identity only |
| Meta reporting conversions | Three reporting-only rules | Creation still returns Meta subcode `1760020`; no broader fallback rule created |
| Dispatcher kill switch | Disabled execution `cefa-parent-offline-conversion-dispatch-gfmdh` | Zero inspected, validated, accepted, failed, or retried |
| Existing inquiry conversions | Current Google website inquiry and Meta `Inquiry Submit` | Preserve unchanged |

## Repository Implementation

### Implemented

- Immutable identity and lifecycle models.
- CEFA stage normalization and approved-stage eligibility.
- Email/phone normalization and SHA-256 helpers.
- Secret-backed HMAC identity and transaction-ID primitives.
- Initial-baseline non-uploadability.
- Multi-school parent-stage deduplication primitives.
- First-positive-stage enforcement.
- Read-only GreenRope field/phase dictionary checks.
- Read-only GreenRope polling primitives with retry/backoff and bounded
  concurrency.
- Missing GreenRope identity-field readiness blocking.
- Dedicated restricted dataset DDL for
  `cefa_parent_activation_restricted`.
- Lifecycle, match-key, outbox, delivery-attempt, quarantine, lease, and
  accepted-lock persistence primitives.
- Google Data Manager event/diagnostic adapter.
- Meta CAPI event adapter.
- Platform identifier, consent, destination, age, and match-path safety checks.
- Cloud Run poller, dispatcher, and diagnostics entrypoints and deployment
  manifests.
- Restricted dataset deployment with narrowed IAM.
- Exact 52-group GreenRope parent-school allowlist.
- BigQuery batching, stable insert IDs, and retry behavior.
- Recursive PII/log guards with an explicit governed opaque-ID allowlist.
- Three secondary Google CRM conversion actions and non-biddable goal safety.
- Explicit current Form 4 UUID-to-GreenRope group map for 52 CEFA schools.
- HMAC-only Form 4 identity inbox and prospective WordPress polling capture.
- Deterministic identity binder with delayed-GreenRope retry behavior.
- Five-minute capture and 15-minute binder Cloud Scheduler jobs with
  job-specific Cloud Run Invoker permissions.
- Dedicated production-identity Google Data Manager validator permanently
  locked to synthetic `validateOnly=true` requests.
- Dedicated Meta Test Events runner restricted to approved CRM events,
  synthetic identity, and a required `TEST...` event code.
- Disabled-mode lifecycle, dispatcher, and diagnostics schedules.
- Focused automated test suite: 69 passing tests on 2026-07-23.

Relevant implementation commits at the time of this report:

| Commit | Scope |
|---|---|
| `0724ba6` | Parent CRM activation core |
| `5d7e524` | Google and Meta platform adapters |
| `e28780c` | Restricted warehouse contract |
| `deabc19` | Read-only GreenRope lifecycle adapter |
| `0f34862` | Activation safety hardening |
| `89b5a96` | Final immediate-rollout blueprint |
| `fa7846d` | Platform setup tooling |
| `19b19ff` | Cloud runtime and orchestration |
| `60ce312` | Google goal and delivery hardening |
| `ef24fef` | Parent-school GreenRope allowlist |
| `5ba8d72` | Batched BigQuery inserts |
| `0f80982` | Governed opaque-ID PII-guard fix |
| `1e31bbf` | Parent Form 4 identity bridge and school map |
| `c0bb015` | Prospective Form 4 identity capture |
| `38d9c20` | Delayed GreenRope identity-match retry behavior |
| `a24df2a` | Production-identity Google Data Manager validator |
| `2a89430` | Synthetic Meta Test Events runner |

### Pending

- GreenRope field creation.
- GreenRope write-mode activation after field creation and controlled
  write/read-back.
- One controlled inquiry and exclusion from business reporting.
- Three Meta reporting custom conversions after Meta registers the custom
  event types in its live registry.
- An approved per-record consent/eligibility source or inherited-policy
  decision; the runtime currently fails closed on `unknown`.
- Prospective lifecycle poller activation after identity readiness.
- Production activation and acceptance monitoring.

### Blocked

Production dispatch is blocked by deterministic prerequisites, not by calendar
waiting:

1. Live GreenRope does not have `cefa_event_id`.
2. Live GreenRope does not have `cefa_form_entry_id`.
3. The identity binder is deployed but GreenRope write mode is intentionally
   disabled until the field contract exists and a controlled write/read-back
   passes.
4. The controlled identity test has not run.
5. Meta Test Events passed, but custom-conversion creation still returns Meta
   subcode `1760020` because test events have not entered the live event
   registry. No production event has been manufactured to bypass this.
6. Per-record consent/eligibility is `unknown` and therefore fail-closed.

## Identity Handoff Requirement

The production identity must be:

```text
Form 4 field 32.4 -> GreenRope cefa_event_id
Gravity Forms entry.id -> GreenRope cefa_form_entry_id
```

`cefa_event_id` must resolve to exactly one confirmed Form 4 entry.
`cefa_form_entry_id` must identify that same entry. Missing or conflicting
identity quarantines only that CRM record.

CEFA's selected integration is the isolated Form 4 capture and GreenRope
identity binder. It does not alter the existing Gravity Forms feed, School
Manager, KinderTales, Supabase, GTM, or current conversion events. The binder
will be enabled only after GreenRope's field dictionary exposes both fields
and the controlled test proves an exact read-back.

## KinderTales Separation

KinderTales is the parent business-delivery path. GreenRope is the lifecycle
source for this offline-conversion rollout. They are separate:

```text
Form 4 -> School Manager -> KinderTales
Form 4 -> approved identity handoff -> GreenRope -> lifecycle activation
```

The activation poller and dispatcher must be asynchronous. A failure or kill
switch in the GreenRope/platform path must not block or retry the KinderTales
submission path.

## Platform Destinations

### Google

Created actions:

- `7695582127` - `CEFA | Parent | CRM Tour Scheduled | GOOGLE`
- `7695186674` - `CEFA | Parent | CRM Tour Completed Candidate | GOOGLE`
- `7695186677` - `CEFA | Parent | CRM Closed Won | GOOGLE`

Read-back on 2026-07-23 confirmed all three are:

- secondary;
- count `ONE`;
- no monetary value;
- excluded from account-default goals;
- not used by bidding.

Google returned the action origin as `WEBSITE`. Safety is enforced using each
action's actual category/origin pair: the corresponding customer goal is
non-biddable, campaign biddable-goal count is zero, and custom-goal inclusion
count is zero.

### Meta

Events to test and activate:

- `CEFA_CRM_TourScheduled`
- `CEFA_CRM_TourCompletedCandidate`
- `CEFA_CRM_ClosedWon`

Create custom conversions for reporting only. Do not select them as ad-set
optimization events. Do not send `Inquiry Submit` from the CRM service.

## Approved Immediate Execution Order

1. Create and populate the two GreenRope identity fields.
2. Run one controlled Form 4 inquiry.
3. Prove Gravity Forms, GreenRope, KinderTales, and existing conversions all
   agree.
4. Keep the three passed Google Data Manager validations and secondary-action
   read-back as the Google activation gate.
5. Create the three Meta reporting custom conversions as soon as Meta exposes
   the tested custom event types to the live rule registry.
6. Resolve the fail-closed consent/eligibility decision.
7. Enable prospective polling and production dispatch.
8. Monitor duplicates, quarantine reasons, delivery diagnostics, PII guards,
    and existing inquiry continuity.

No seven-day, 14-day, or bounded-pilot delay follows these checks.

## Production Acceptance Record

Complete this table during activation:

| Check | Status | Evidence reference |
|---|---|---|
| GreenRope identity fields created | Pending | |
| Identity capture/binder deployed | Passed, write-gated | Five-minute capture and 15-minute binder schedules enabled; GreenRope write flag false |
| Controlled Form 4 event ID match | Pending | |
| Controlled Form entry ID match | Pending | |
| Controlled KinderTales delivery | Pending | |
| Existing inquiry conversion fires once | Pending | |
| Test excluded from business reporting | Pending | |
| Restricted dataset IAM passed | Passed | Restricted dataset ACL limited to activation writer and designated owners |
| Google actions created and read back | Passed | Action IDs `7695582127`, `7695186674`, `7695186677`; secondary/non-biddable |
| Google `validateOnly` passed for all actions | Passed | Execution `cefa-parent-google-data-manager-validate-wqsxk`; three request IDs; zero failures |
| Meta Test Events passed for all events | Passed | Execution `cefa-parent-meta-test-events-ckkft`; three received; zero messages |
| Meta reporting custom conversions created | Pending on Meta live registry | API subcode `1760020`; no fallback or production test event created |
| Initial baseline committed non-uploadable | Passed | Execution `cefa-parent-crm-lifecycle-refresh-hvh5p`; 22,328/22,328 rows |
| Poller production schedule enabled | Passed, runtime disabled | `cefa-parent-crm-lifecycle-refresh-15m` |
| Dispatcher production schedule enabled | Passed, sending disabled | `cefa-parent-offline-conversion-dispatch-5m` |
| Dispatcher production schedule enabled | Pending | |
| First eligible Google outcome accepted | Pending | |
| First eligible Meta outcome accepted | Pending | |
| Duplicate accepted transaction IDs = 0 | Pending | |
| Baseline uploads = 0 | Passed to date | Zero lifecycle, outbox, and delivery rows after baseline |
| Existing inquiry continuity passed | Pending | |
| PII scan passed | Passed for schema/runtime/tests | No prohibited columns; recursive guard and 58-test suite passed |
| Kill switch passed | Passed | Execution `cefa-parent-offline-conversion-dispatch-gfmdh`; all counters zero |

## Operational Stop Rule

Disable the dispatcher immediately for a duplicate accepted transaction ID, PII
leakage, baseline upload, wrong stage, inquiry-conversion interference,
KinderTales regression, biddable Google CRM action, or Meta CRM optimization
selection. Preserve the ledger and delivery history for diagnosis.

## Change Log

| Date | Change |
|---|---|
| 2026-07-23 | Replaced calendar-based waiting gates with exact per-record eligibility and immediate production delivery after deterministic identity and platform tests |
| 2026-07-23 | Recorded that GreenRope identity fields and a WordPress GreenRope writer are absent |
| 2026-07-23 | Separated School Manager/KinderTales delivery from GreenRope lifecycle activation |
| 2026-07-23 | Locked initial restricted dataset to `cefa_parent_activation_restricted` and removed dashboard-object rollout |
| 2026-07-23 | Deployed restricted BigQuery contract and disabled Cloud Run v5 runtime |
| 2026-07-23 | Established 22,328-row non-uploadable GreenRope baseline with zero activation rows |
| 2026-07-23 | Created/read back three secondary, non-biddable Google CRM reporting actions |
| 2026-07-23 | Proved dispatcher kill switch; documented Google account-access, Meta Test Events, GreenRope identity, and consent blockers |
| 2026-07-23 | Deployed isolated HMAC-only prospective Form 4 identity capture and deterministic GreenRope binder |
| 2026-07-23 | Enabled five-minute capture and 15-minute binder schedules while keeping GreenRope writes and all platform delivery disabled |
| 2026-07-23 | Changed delayed GreenRope opportunity creation from permanent quarantine to retryable matching |
| 2026-07-23 | Added the runtime service account to Google Ads and passed all three Data Manager validation-only requests |
| 2026-07-23 | Reconfirmed all Google CRM actions are secondary, non-biddable, and absent from campaign/custom goals |
| 2026-07-23 | Passed all three Meta Test Events under the production runtime using synthetic identity only |
| 2026-07-23 | Enabled disabled-mode lifecycle, dispatcher, and diagnostics schedules; no platform sending enabled |
| 2026-07-23 | Reconfirmed restricted warehouse safety after scheduling: 22,328 baseline snapshots; zero lifecycle events, outbox rows, or delivery attempts |
