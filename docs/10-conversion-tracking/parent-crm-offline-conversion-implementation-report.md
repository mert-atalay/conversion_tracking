# Parent CRM Offline Conversion Implementation Report

**Report date:** 2026-07-23
**Rollout:** CEFA parent CRM offline conversions
**Approved mode:** Immediate per-record production rollout after deterministic tests
**Current production state:** Infrastructure and non-uploadable baseline deployed;
production dispatch disabled on deterministic blockers
**Blueprint:** `docs/superpowers/plans/2026-07-23-parent-crm-offline-conversion-activation-blueprint.md`

## Executive Status

The restricted warehouse, GreenRope poller, outbox dispatcher, diagnostics
runtime, and three Google reporting actions are deployed. A successful
2026-07-23 baseline stored `22,328` unique current-state opportunities as
`baseline_non_uploadable`; it created zero lifecycle events, outbox rows, or
delivery attempts. A disabled-dispatcher execution also processed and sent
zero rows.

Production sending remains disabled. The live GreenRope opportunity schema
lacks the two exact identity fields required to connect a CRM outcome safely
to one Form 4 submission. Google Data Manager validation is blocked until the
runtime service account is added to the Google Ads account. The new Meta
custom event types must pass Test Events before their reporting custom
conversions can be created. Per-record consent/eligibility remains fail-closed
as `unknown`.

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
| Container | `parent-crm-activation:20260723-full-rollout-v5` |
| Image digest | `sha256:bd0873b5a1923f57c7f38ba3096343d90845ecb5ce40b918d9098a7768b31ba2` |
| Poller job | `cefa-parent-crm-lifecycle-refresh` |
| Dispatcher job | `cefa-parent-offline-conversion-dispatch` |
| Diagnostics job | `cefa-parent-conversion-diagnostics` |
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
| Form handoff | Feed `4` is `CEFA Dashboard Parent Inquiry Handoff` to `cefa-brain.vercel.app` | Existing |
| KinderTales | School Manager independently performs KinderTales business delivery | Existing and out of activation path |
| WordPress GreenRope writer | Live plugin review found no GreenRope writer in CEFA Conversion Tracking or School Manager | Not found |
| GreenRope event identity | Live field dictionary lacks `cefa_event_id` | Blocked |
| GreenRope entry identity | Live field dictionary lacks `cefa_form_entry_id` | Blocked |
| GreenRope history | Existing API extraction represents current state | Initial baseline stored; prospective polling remains disabled |
| GreenRope scope | 52 approved parent-school groups; `TEST - Systems` excluded | Enforced by poller allowlist |
| Restricted warehouse | `marketing-api-488017.cefa_parent_activation_restricted` | Deployed with narrowed dataset IAM |
| Initial baseline | 22,328 unique snapshots in one poll run | 100% `baseline_non_uploadable`; zero activation rows |
| Cloud Run runtime | Poller, dispatcher, and diagnostics jobs on v5 image | Deployed; send switches disabled |
| Google CRM actions | Actions `7695582127`, `7695186674`, and `7695186677` | Created, secondary, non-biddable, no campaign/custom-goal inclusion |
| Google Data Manager API | Enabled in project `marketing-api-488017` | API enabled; `validateOnly` blocked by destination-account access |
| Meta CRM events/conversions | Three planned CRM reporting outcomes | Adapters deployed; Test Events/custom conversions pending |
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
- Focused automated test suite: 58 passing tests on 2026-07-23.

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

### Pending

- GreenRope field creation.
- A confirmed writer/handoff for Form 4 identity into GreenRope.
- One controlled inquiry and exclusion from business reporting.
- Google Ads user access for the runtime service account.
- Three Google Data Manager `validateOnly` calls.
- Three Meta Test Events and three reporting custom conversions.
- An approved per-record consent/eligibility source or inherited-policy
  decision; the runtime currently fails closed on `unknown`.
- Prospective poller schedule.
- Production activation and acceptance monitoring.

### Blocked

Production dispatch is blocked by deterministic prerequisites, not by calendar
waiting:

1. Live GreenRope does not have `cefa_event_id`.
2. Live GreenRope does not have `cefa_form_entry_id`.
3. No verified Form 4-to-GreenRope writer/handoff exists.
4. The controlled identity test has not run.
5. `marketing-cefa-795@marketing-api-488017.iam.gserviceaccount.com` is not a
   Google Ads user in account `4159217891`; all three Data Manager validation
   calls return permission denied.
6. The current Google Ads developer token has Explorer access, so it cannot
   create the required user invitation through the API.
7. Google `validateOnly=true` has not passed.
8. Meta Test Events has not passed, so Meta does not yet recognize the three
   new custom event types for custom-conversion creation.
9. Per-record consent/eligibility is `unknown` and therefore fail-closed.

## Identity Handoff Requirement

The production identity must be:

```text
Form 4 field 32.4 -> GreenRope cefa_event_id
Gravity Forms entry.id -> GreenRope cefa_form_entry_id
```

`cefa_event_id` must resolve to exactly one confirmed Form 4 entry.
`cefa_form_entry_id` must identify that same entry. Missing or conflicting
identity quarantines only that CRM record.

The integration that writes these values still needs to be selected and proven.
Documentation must not imply that School Manager or the CEFA Conversion
Tracking plugin currently writes to GreenRope.

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
4. Add the runtime service account as a Standard user in Google Ads account
   `415-921-7891`.
5. Pass all three Google Data Manager `validateOnly=true` requests.
6. Pass all three Meta Test Events and create reporting custom conversions.
7. Resolve the fail-closed consent/eligibility decision.
8. Enable prospective polling and production dispatch.
9. Monitor duplicates, quarantine reasons, delivery diagnostics, PII guards,
    and existing inquiry continuity.

No seven-day, 14-day, or bounded-pilot delay follows these checks.

## Production Acceptance Record

Complete this table during activation:

| Check | Status | Evidence reference |
|---|---|---|
| GreenRope identity fields created | Pending | |
| Identity writer/handoff deployed | Pending | |
| Controlled Form 4 event ID match | Pending | |
| Controlled Form entry ID match | Pending | |
| Controlled KinderTales delivery | Pending | |
| Existing inquiry conversion fires once | Pending | |
| Test excluded from business reporting | Pending | |
| Restricted dataset IAM passed | Passed | Restricted dataset ACL limited to activation writer and designated owners |
| Google actions created and read back | Passed | Action IDs `7695582127`, `7695186674`, `7695186677`; secondary/non-biddable |
| Google `validateOnly` passed for all actions | Pending | |
| Meta Test Events passed for all events | Pending | |
| Meta reporting custom conversions created | Pending | |
| Initial baseline committed non-uploadable | Passed | Execution `cefa-parent-crm-lifecycle-refresh-hvh5p`; 22,328/22,328 rows |
| Poller production schedule enabled | Pending | |
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
