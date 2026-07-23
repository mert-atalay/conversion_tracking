# Parent CRM Offline Conversion Data Contract

**Contract version:** `parent_crm_offline_conversion_v1`
**Effective date:** 2026-07-23
**Scope:** `cefa.ca` Gravity Forms Form 4 prospective CRM outcomes
**Dataset:** `marketing-api-488017.cefa_parent_activation_restricted`

## Purpose

This contract governs the restricted identity, lifecycle, activation, and
delivery data used to send CEFA parent CRM outcomes to Google Ads and Meta.
It does not change the existing Form 4 inquiry event, School Manager,
KinderTales, campaign bidding, or reporting KPIs.

## Dataset Boundary

Use only:

```text
marketing-api-488017.cefa_parent_activation_restricted
```

The dataset must:

- be located in `US`;
- be accessible only to the activation runtime and designated administrators;
- not grant access to dashboard or general reporting identities;
- not reuse the existing shared `cefa_restricted` dataset;
- not publish an initial dashboard dataset object.

Aggregate monitoring may be materialized later in
`mart_cefa_growth_intelligence` after a separate access and privacy review.

## Source Identity Contract

| Source | Field | Meaning | Rule |
|---|---|---|---|
| Gravity Forms Form 4 | `32.4` | `cefa_event_id` | Exact submission identity |
| Gravity Forms server | entry `id` | `cefa_form_entry_id` | Exact form record identity |
| Gravity Forms Form 4 | `32.1` | `school_uuid` | Original submitted school |
| Gravity Forms Form 4 | `35-46` | Attribution evidence | Preserve existing semantics |

`cefa_event_id` must resolve to exactly one confirmed Form 4 submission.
`cefa_form_entry_id`, when evaluated, must identify that same submission.
Fuzzy identity matching is prohibited.

## Approved Stage Contract

| Raw GreenRope outcome | Canonical stage | Activation |
|---|---|---|
| `tour scheduled` | `tour_scheduled` | Send |
| `post tour` | `tour_completed_candidate` | Send |
| `enrollment (closed won)` | `crm_closed_won` | Send |
| `nurturing` | none | Non-send |
| lost outcome | none | Non-send |
| missed outcome | none | Non-send |
| unmapped outcome | none | Quarantine |

No other positive stage is permitted in v1.

## Lifecycle Semantics

- The first complete GreenRope snapshot is permanently
  `baseline_non_uploadable`.
- A polling transition receives
  `timestamp_quality=poll_observed`.
- `stage_occurred_at` is the first time CEFA observes the transition.
- A verified future workflow timestamp may replace polling uncertainty without
  changing event identity.
- Lifecycle history is preserved at opportunity grain.
- Platform activation deduplicates at Form 4 event and canonical-stage grain.
- Multiple school opportunities for one Form 4 event create one platform
  conversion per approved stage.
- Only the first positive occurrence of an approved stage is uploadable in v1.

## Restricted Tables

### `parent_crm_lifecycle_state_snapshot`

Purpose: append-only observed GreenRope state, including the non-uploadable
initial baseline.

Required columns:

```text
snapshot_at TIMESTAMP
snapshot_date DATE
poll_run_id STRING
opportunity_id_hmac STRING
governed_lead_id_hmac STRING
form4_event_id STRING
form_entry_id STRING
greenrope_group_id STRING
school_uuid STRING
opportunity_created_at TIMESTAMP
source_modified_at TIMESTAMP
source_modified_at_quality STRING
raw_phase STRING
canonical_stage STRING
stage_mapping_version STRING
is_initial_baseline BOOL
baseline_status STRING
attribution_platform STRING
has_gclid BOOL
has_gbraid BOOL
has_wbraid BOOL
has_fbc BOOL
has_fbp BOOL
has_email_hash BOOL
has_phone_hash BOOL
pii_redacted BOOL
loaded_at TIMESTAMP
```

Partition by `snapshot_date`. Cluster by `opportunity_id_hmac`,
`canonical_stage`, and `attribution_platform`.

### `parent_crm_lifecycle_event`

Purpose: append-only prospective transition history and record-level
eligibility/quarantine result.

Required columns:

```text
lifecycle_event_id STRING
opportunity_id_hmac STRING
stage_sequence INT64
previous_stage STRING
canonical_stage STRING
raw_phase STRING
stage_occurred_at TIMESTAMP
first_observed_at TIMESTAMP
previous_observed_at TIMESTAMP
timestamp_quality STRING
timestamp_uncertainty_seconds INT64
event_source STRING
is_initial_baseline BOOL
form4_event_id STRING
form_entry_id STRING
school_uuid STRING
attribution_platform STRING
eligibility_status STRING
eligibility_reasons ARRAY<STRING>
quarantine_status STRING
quarantine_reason STRING
created_at TIMESTAMP
```

Partition by `DATE(stage_occurred_at)`. Cluster by `opportunity_id_hmac`,
`canonical_stage`, and `eligibility_status`.

### `parent_crm_match_key`

Purpose: restricted, expiring platform match evidence.

Required columns:

```text
captured_date DATE
form4_event_id STRING
opportunity_id_hmac STRING
governed_lead_id_hmac STRING
email_sha256 STRING
phone_sha256 STRING
gclid STRING
gbraid STRING
wbraid STRING
fbc STRING
fbp STRING
click_id_captured_at TIMESTAMP
user_data_captured_at TIMESTAMP
match_key_source STRING
consent_status STRING
expires_at TIMESTAMP
loaded_at TIMESTAMP
```

Partition by `captured_date` with a maximum 100-day partition expiration.
Cluster by `form4_event_id` and `opportunity_id_hmac`.

Only real captured click/cookie values are permitted. Do not construct `fbc`,
`fbp`, click times, or session attributes from UTMs.

### `parent_conversion_outbox`

Purpose: one idempotent delivery instruction per platform, destination, and
parent-stage transaction.

Required columns:

```text
outbox_id STRING
selected_lifecycle_event_id STRING
form4_event_id STRING
activation_subject_id_hmac STRING
activation_identity_scope STRING
canonical_stage STRING
source_lifecycle_event_count INT64
source_is_initial_baseline BOOL
school_uuid STRING
platform STRING
destination_account_id STRING
destination_action_key STRING
platform_event_name STRING
transaction_id STRING
event_timestamp TIMESTAMP
event_value NUMERIC
currency STRING
match_key_ref STRING
activation_mode STRING
delivery_status STRING
quarantine_status STRING
quarantine_reason STRING
attempt_count INT64
next_attempt_at TIMESTAMP
lease_owner STRING
lease_expires_at TIMESTAMP
accepted_at TIMESTAMP
accepted_lock_id STRING
last_error_code STRING
last_error_message STRING
created_at TIMESTAMP
updated_at TIMESTAMP
```

Partition by `DATE(created_at)`. Cluster by `platform`,
`destination_action_key`, `delivery_status`, and `transaction_id`.

Allowed activation modes:

- `disabled`
- `validate_only`
- `meta_test`
- `secondary_production`

Allowed delivery states:

- `blocked`
- `quarantined`
- `queued`
- `leased`
- `validation_passed`
- `test_accepted`
- `processing`
- `accepted`
- `retryable_failure`
- `permanent_failure`
- `expired`

An accepted row is immutable. `mark_accepted` must require the current,
unexpired lease owner and write a stable accepted lock.

### `parent_conversion_delivery_attempt`

Purpose: redacted platform request and diagnostic audit.

Required columns:

```text
delivery_attempt_id STRING
outbox_id STRING
transaction_id STRING
platform STRING
destination_action_key STRING
attempt_number INT64
attempt_started_at TIMESTAMP
attempt_finished_at TIMESTAMP
delivery_status STRING
response_status_code INT64
request_id STRING
platform_event_id STRING
is_retryable BOOL
error_code STRING
error_message STRING
warning_count INT64
accepted_at TIMESTAMP
created_at TIMESTAMP
```

Raw requests and responses are prohibited. Error text must be recursively
sanitized before persistence.

## Identifier Construction

HMAC key material lives in Secret Manager and never appears in code, SQL,
tables, or logs.

```text
lifecycle_event_id =
  HMAC(source_account | opportunity_identity | canonical_stage | stage_sequence)

transaction_id =
  HMAC(
    source_account
    | form4_event
    | form4_event_id
    | canonical_stage
    | approved_occurrence
  )

outbox_id =
  HMAC(platform | destination_action_key | transaction_id)
```

Persist only HMAC outputs. Do not store raw CRM opportunity or lead IDs in the
activation dataset.

## Match-Key Rules

### Google

Eligible match paths:

- valid `gclid`, `gbraid`, or `wbraid`; or
- eligible normalized SHA-256 email/phone for enhanced lead matching.

The dispatcher enforces platform age limits before building the payload.
The destination registry stores the bare numeric `UPLOAD_CLICKS` conversion
action ID and verified action type.

### Meta

Require at least one real matching path:

- eligible normalized SHA-256 email/phone; or
- genuinely captured `fbc` or `fbp`.

An HMAC `external_id` is stable CEFA identity and idempotency evidence; it is not
by itself sufficient evidence that Meta can match the person.

## Normalization

Email:

```text
trim -> lowercase -> validate -> SHA-256
```

Phone:

```text
trim -> normalize to E.164 using approved default country -> validate -> SHA-256
```

Pre-hashed values must be lowercase 64-character hexadecimal strings. Invalid
values are quarantined rather than re-hashed or sent.

## PII Prohibition

The following must not exist in marketing table columns, nested payloads,
logs, delivery attempts, or diagnostics:

- raw first or last name;
- raw email;
- raw phone;
- child name or child details;
- date of birth;
- street or mailing address;
- free-text notes;
- IP address;
- raw CRM payload;
- raw platform payload;
- access token, cookie secret, or HMAC key.

Column and key scanning must normalize case and separators and recurse into
nested objects. Error messages must be redacted before storage.

## Quarantine Contract

Every ineligible record receives:

```text
quarantine_status
quarantine_reason
first_quarantined_at
last_evaluated_at
recoverable flag
```

Correcting identity or destination evidence may release a recoverable
quarantine into the same deterministic outbox identity. A released record must
not receive a new transaction ID.

## Monitoring Contract

Initial monitoring is aggregate and operations-facing. It may include:

- records observed;
- transitions detected;
- eligible and quarantined counts;
- quarantine reasons;
- platform match-path coverage;
- queue depth;
- delivery status;
- retry/permanent-failure rates;
- duplicate accepted transaction IDs;
- baseline upload attempts;
- processing latency.

No dashboard dataset object is created in the initial rollout.

## Retention

| Data | Retention |
|---|---|
| Raw click/cookie identifiers | Maximum 100 days |
| Normalized contact hashes | Restricted retention only as long as platform matching/recovery requires |
| Lifecycle HMAC identities | Retain for audit and idempotency |
| Delivery metadata | Retain for audit and diagnostics |
| Raw API payloads | Never persist |

## Recovery And Kill Switch

The global dispatcher kill switch stops new Google and Meta sends while
preserving polling, the lifecycle ledger, outbox, Form 4, existing inquiry
conversions, School Manager, and KinderTales.

Retryable failures retain the same outbox and transaction IDs. Permanent
failures remain visible and require a reviewed correction before release.

## Versioning

Any change to stage meaning, identity scope, source authority, platform
destination, deduplication grain, retention, or PII policy requires a new
reviewed contract version. GreenRope phases default to non-send when they are
not present in the approved phase reference file.
