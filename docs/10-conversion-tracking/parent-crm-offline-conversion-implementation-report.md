# Parent CRM Offline Conversion Implementation Report

**Report date:** 2026-07-23
**Rollout:** CEFA parent CRM offline conversions
**Approved mode:** Immediate per-record production rollout after deterministic tests
**Current production state:** Not activated
**Blueprint:** `docs/superpowers/plans/2026-07-23-parent-crm-offline-conversion-activation-blueprint.md`

## Executive Status

The repository now contains the core lifecycle, restricted-warehouse,
GreenRope-read, and platform-payload foundations. Production sending is not yet
enabled. The live GreenRope opportunity schema lacks the two exact identity
fields required to connect a CRM outcome safely to one Form 4 submission, and
the planned Google/Meta CRM destinations have not been created or validated.

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

No platform action, campaign, conversion goal, WordPress form, School Manager
flow, KinderTales delivery, or GreenRope field was changed while producing this
report.

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
| GreenRope history | Existing API extraction represents current state | Prospective ledger still required |
| Google CRM actions | Three planned `UPLOAD_CLICKS` actions | Do not exist |
| Google Data Manager API | Project `marketing-api-488017` | Not enabled |
| Meta CRM events/conversions | Three planned CRM reporting outcomes | Do not exist |
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
- Focused automated tests for the implemented parent-activation foundation.

Relevant implementation commits at the time of this report:

| Commit | Scope |
|---|---|
| `0724ba6` | Parent CRM activation core |
| `5d7e524` | Google and Meta platform adapters |
| `e28780c` | Restricted warehouse contract |
| `deabc19` | Read-only GreenRope lifecycle adapter |
| `0f34862` | Activation safety hardening |

### Pending

- GreenRope field creation.
- A confirmed writer/handoff for Form 4 identity into GreenRope.
- One controlled inquiry and exclusion from business reporting.
- Dedicated restricted dataset deployment and IAM verification.
- Dispatcher orchestration, diagnostics, runtime packaging, and deployment.
- Global and platform-specific kill-switch verification.
- Google Data Manager API enablement.
- Three Google conversion-action creates, `validateOnly` calls, and settings
  read-back.
- Three Meta Test Events and three reporting custom conversions.
- Initial non-uploadable GreenRope baseline.
- Production activation and acceptance monitoring.

### Blocked

Production dispatch is blocked by deterministic prerequisites, not by calendar
waiting:

1. Live GreenRope does not have `cefa_event_id`.
2. Live GreenRope does not have `cefa_form_entry_id`.
3. No verified Form 4-to-GreenRope writer/handoff exists.
4. The controlled identity test has not run.
5. Google CRM actions do not exist.
6. Google Data Manager API is not enabled.
7. Google `validateOnly=true` has not passed.
8. Meta Test Events has not passed.
9. Restricted runtime and dispatcher are not deployed.

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

Actions to create:

- `CEFA | Parent | CRM Tour Scheduled | GOOGLE`
- `CEFA | Parent | CRM Tour Completed Candidate | GOOGLE`
- `CEFA | Parent | CRM Closed Won | GOOGLE`

All must be:

- `UPLOAD_CLICKS`;
- secondary;
- count `ONE`;
- no monetary value;
- excluded from account-default goals;
- not used by bidding.

### Meta

Events to test and activate:

- `CEFA_CRM_TourScheduled`
- `CEFA_CRM_TourCompletedCandidate`
- `CEFA_CRM_ClosedWon`

Create custom conversions for reporting only. Do not select them as ad-set
optimization events. Do not send `Inquiry Submit` from the CRM service.

## Approved Immediate Execution Order

1. Deploy the restricted dataset and disabled runtime.
2. Create and populate the two GreenRope identity fields.
3. Run one controlled Form 4 inquiry.
4. Prove Gravity Forms, GreenRope, KinderTales, and existing conversions all
   agree.
5. Enable Google Data Manager API.
6. Create/read back the Google actions and pass `validateOnly=true`.
7. Pass all three Meta Test Events and create reporting custom conversions.
8. Capture the permanently non-uploadable GreenRope baseline.
9. Enable prospective polling and production dispatch.
10. Monitor duplicates, quarantine reasons, delivery diagnostics, PII guards,
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
| Restricted dataset IAM passed | Pending | |
| Google actions created and read back | Pending | |
| Google `validateOnly` passed for all actions | Pending | |
| Meta Test Events passed for all events | Pending | |
| Meta reporting custom conversions created | Pending | |
| Initial baseline committed non-uploadable | Pending | |
| Poller production schedule enabled | Pending | |
| Dispatcher production schedule enabled | Pending | |
| First eligible Google outcome accepted | Pending | |
| First eligible Meta outcome accepted | Pending | |
| Duplicate accepted transaction IDs = 0 | Pending | |
| Baseline uploads = 0 | Pending | |
| Existing inquiry continuity passed | Pending | |
| PII scan passed | Pending | |
| Kill switch passed | Pending | |

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
