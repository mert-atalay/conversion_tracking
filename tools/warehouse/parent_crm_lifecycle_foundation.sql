-- CEFA parent CRM offline-conversion restricted warehouse contract.
--
-- Scope: cefa.ca parent Form 4 -> GreenRope prospective lifecycle activation.
-- Dataset IAM must be restricted to the activation runtime and designated
-- administrators before this contract is applied. No dashboard objects are
-- created here.

CREATE SCHEMA IF NOT EXISTS `marketing-api-488017.cefa_parent_activation_restricted`
OPTIONS (
  location = 'US',
  description = 'Restricted CEFA parent CRM activation data. Not a reporting or dashboard dataset.'
);

CREATE TABLE IF NOT EXISTS `marketing-api-488017.cefa_parent_activation_restricted.parent_crm_lifecycle_state_snapshot` (
  snapshot_at TIMESTAMP NOT NULL,
  snapshot_date DATE NOT NULL,
  poll_run_id STRING NOT NULL,
  opportunity_id_hmac STRING NOT NULL,
  governed_lead_id_hmac STRING,
  form4_event_id STRING,
  form_entry_id STRING,
  greenrope_group_id STRING,
  school_uuid STRING,
  opportunity_created_at TIMESTAMP,
  source_modified_at TIMESTAMP,
  source_modified_at_quality STRING,
  raw_phase STRING,
  canonical_stage STRING,
  stage_mapping_version STRING NOT NULL,
  is_initial_baseline BOOL NOT NULL,
  baseline_status STRING NOT NULL,
  attribution_platform STRING,
  has_gclid BOOL NOT NULL,
  has_gbraid BOOL NOT NULL,
  has_wbraid BOOL NOT NULL,
  has_fbc BOOL NOT NULL,
  has_fbp BOOL NOT NULL,
  has_email_hash BOOL NOT NULL,
  has_phone_hash BOOL NOT NULL,
  pii_redacted BOOL NOT NULL,
  loaded_at TIMESTAMP NOT NULL
)
PARTITION BY snapshot_date
CLUSTER BY opportunity_id_hmac, canonical_stage, attribution_platform
OPTIONS (
  description = 'Restricted observed GreenRope state. Initial snapshot records are permanently baseline_non_uploadable.'
);

CREATE TABLE IF NOT EXISTS `marketing-api-488017.cefa_parent_activation_restricted.parent_crm_lifecycle_event` (
  lifecycle_event_id STRING NOT NULL,
  opportunity_id_hmac STRING NOT NULL,
  stage_sequence INT64 NOT NULL,
  previous_stage STRING,
  canonical_stage STRING NOT NULL,
  raw_phase STRING,
  stage_occurred_at TIMESTAMP NOT NULL,
  first_observed_at TIMESTAMP NOT NULL,
  previous_observed_at TIMESTAMP,
  timestamp_quality STRING NOT NULL,
  timestamp_uncertainty_seconds INT64,
  event_source STRING NOT NULL,
  is_initial_baseline BOOL NOT NULL,
  form4_event_id STRING,
  form_entry_id STRING,
  school_uuid STRING,
  attribution_platform STRING,
  eligibility_status STRING NOT NULL,
  eligibility_reasons ARRAY<STRING>,
  quarantine_status STRING NOT NULL,
  quarantine_reason STRING,
  created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(stage_occurred_at)
CLUSTER BY opportunity_id_hmac, canonical_stage, eligibility_status
OPTIONS (
  description = 'Restricted prospective lifecycle events. Baseline and unresolved Form 4 identities remain quarantined.'
);

-- Raw click identifiers are restricted, partition-expiring evidence. Contact
-- identifiers are already normalized SHA-256 values before this boundary.
CREATE TABLE IF NOT EXISTS `marketing-api-488017.cefa_parent_activation_restricted.parent_crm_match_key` (
  captured_date DATE NOT NULL,
  form4_event_id STRING NOT NULL,
  opportunity_id_hmac STRING,
  governed_lead_id_hmac STRING,
  email_sha256 STRING,
  phone_sha256 STRING,
  gclid STRING,
  gbraid STRING,
  wbraid STRING,
  fbc STRING,
  fbp STRING,
  click_id_captured_at TIMESTAMP,
  user_data_captured_at TIMESTAMP,
  match_key_source STRING NOT NULL,
  consent_status STRING NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  loaded_at TIMESTAMP NOT NULL
)
PARTITION BY captured_date
CLUSTER BY form4_event_id, opportunity_id_hmac
OPTIONS (
  partition_expiration_days = 100,
  description = 'Restricted, expiring parent activation match keys. Access is denied to reporting identities.'
);

CREATE TABLE IF NOT EXISTS `marketing-api-488017.cefa_parent_activation_restricted.parent_conversion_outbox` (
  outbox_id STRING NOT NULL,
  selected_lifecycle_event_id STRING NOT NULL,
  form4_event_id STRING NOT NULL,
  activation_subject_id_hmac STRING NOT NULL,
  activation_identity_scope STRING NOT NULL,
  canonical_stage STRING NOT NULL,
  source_lifecycle_event_count INT64 NOT NULL,
  source_is_initial_baseline BOOL NOT NULL,
  school_uuid STRING NOT NULL,
  platform STRING NOT NULL,
  destination_account_id STRING NOT NULL,
  destination_action_key STRING NOT NULL,
  platform_event_name STRING NOT NULL,
  transaction_id STRING NOT NULL,
  event_timestamp TIMESTAMP NOT NULL,
  event_value NUMERIC,
  currency STRING,
  match_key_ref STRING,
  activation_mode STRING NOT NULL,
  delivery_status STRING NOT NULL,
  quarantine_status STRING NOT NULL,
  quarantine_reason STRING,
  attempt_count INT64 NOT NULL,
  next_attempt_at TIMESTAMP,
  lease_owner STRING,
  lease_expires_at TIMESTAMP,
  accepted_at TIMESTAMP,
  accepted_lock_id STRING,
  last_error_code STRING,
  last_error_message STRING,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY platform, destination_action_key, delivery_status, transaction_id
OPTIONS (
  description = 'Restricted idempotent outbox. Baseline rows are permanently blocked; accepted rows are immutable.'
);

CREATE TABLE IF NOT EXISTS `marketing-api-488017.cefa_parent_activation_restricted.parent_conversion_delivery_attempt` (
  delivery_attempt_id STRING NOT NULL,
  outbox_id STRING NOT NULL,
  transaction_id STRING NOT NULL,
  platform STRING NOT NULL,
  destination_action_key STRING NOT NULL,
  attempt_number INT64 NOT NULL,
  attempt_started_at TIMESTAMP NOT NULL,
  attempt_finished_at TIMESTAMP,
  delivery_status STRING NOT NULL,
  response_status_code INT64,
  request_id STRING,
  platform_event_id STRING,
  is_retryable BOOL,
  error_code STRING,
  error_message STRING,
  warning_count INT64 NOT NULL,
  accepted_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(attempt_started_at)
CLUSTER BY outbox_id, platform, delivery_status
OPTIONS (
  description = 'Restricted redacted delivery audit. Raw platform payloads and match identifiers are prohibited.'
);
