-- CEFA parent CRM offline-conversion restricted warehouse contract.
--
-- Scope: cefa.ca parent Form 4 -> GreenRope prospective lifecycle activation.
-- This contract is additive. It does not update existing dashboard KPIs and it
-- never stores raw contact details, CRM payloads, or unrestricted click IDs.

CREATE SCHEMA IF NOT EXISTS `marketing-api-488017.cefa_restricted`
OPTIONS (
  location = 'US',
  description = 'Restricted CEFA parent CRM activation data. Access is limited to activation runtime identities and designated administrators.'
);

CREATE TABLE IF NOT EXISTS `marketing-api-488017.cefa_restricted.parent_crm_lifecycle_state_snapshot` (
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

ALTER TABLE `marketing-api-488017.cefa_restricted.parent_crm_lifecycle_state_snapshot`
ADD COLUMN IF NOT EXISTS baseline_status STRING;

CREATE TABLE IF NOT EXISTS `marketing-api-488017.cefa_restricted.parent_crm_lifecycle_event` (
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
  description = 'Restricted prospective parent CRM lifecycle events. Rows without exact Form 4 identity remain quarantined.'
);

ALTER TABLE `marketing-api-488017.cefa_restricted.parent_crm_lifecycle_event`
ADD COLUMN IF NOT EXISTS quarantine_reason STRING;

-- Click identifiers and platform-ready hashes are intentionally restricted and
-- expire 100 days after their captured-date partition.
CREATE TABLE IF NOT EXISTS `marketing-api-488017.cefa_restricted.parent_crm_match_key` (
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
  match_key_source STRING NOT NULL,
  consent_status STRING NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  loaded_at TIMESTAMP NOT NULL
)
PARTITION BY captured_date
CLUSTER BY form4_event_id, opportunity_id_hmac
OPTIONS (
  partition_expiration_days = 100,
  description = 'Restricted parent activation match keys. Actual click identifiers and hashed contact identifiers expire after 100 days.'
);

ALTER TABLE `marketing-api-488017.cefa_restricted.parent_crm_match_key`
ADD COLUMN IF NOT EXISTS consent_status STRING;

CREATE TABLE IF NOT EXISTS `marketing-api-488017.cefa_restricted.parent_conversion_outbox` (
  outbox_id STRING NOT NULL,
  selected_lifecycle_event_id STRING NOT NULL,
  form4_event_id STRING NOT NULL,
  activation_subject_id_hmac STRING NOT NULL,
  activation_identity_scope STRING NOT NULL,
  canonical_stage STRING NOT NULL,
  source_lifecycle_event_count INT64 NOT NULL,
  platform STRING NOT NULL,
  destination_account_id STRING NOT NULL,
  destination_action_key STRING NOT NULL,
  platform_event_name STRING NOT NULL,
  transaction_id STRING NOT NULL,
  event_time TIMESTAMP NOT NULL,
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
  description = 'Restricted parent offline-conversion outbox. Deduplicate with form4_event_id, canonical_stage, platform, and destination_action_key; accepted rows are immutable delivery locks.'
);

ALTER TABLE `marketing-api-488017.cefa_restricted.parent_conversion_outbox`
ADD COLUMN IF NOT EXISTS accepted_lock_id STRING;

ALTER TABLE `marketing-api-488017.cefa_restricted.parent_conversion_outbox`
ADD COLUMN IF NOT EXISTS quarantine_reason STRING;

CREATE TABLE IF NOT EXISTS `marketing-api-488017.cefa_restricted.parent_conversion_delivery_attempt` (
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
  description = 'Restricted delivery audit. It retains only request references and outcome diagnostics, never raw match identifiers or contact data.'
);

ALTER TABLE `marketing-api-488017.cefa_restricted.parent_conversion_delivery_attempt`
ADD COLUMN IF NOT EXISTS accepted_at TIMESTAMP;

-- These redacted monitoring views intentionally expose only aggregate counts,
-- statuses, and non-identifying operational metadata. They expose no click IDs,
-- hashes, contact data, Form 4 entry IDs, or platform request payloads.
CREATE OR REPLACE VIEW `marketing-api-488017.mart_cefa_growth_intelligence.v_parent_crm_offline_activation_monitoring_daily`
OPTIONS (
  description = 'Redacted aggregate monitoring for parent CRM offline activation. Not a dashboard KPI contract.'
) AS
SELECT
  DATE(created_at, 'America/Vancouver') AS activity_date,
  platform,
  destination_action_key,
  canonical_stage,
  activation_mode,
  delivery_status,
  quarantine_status,
  COUNT(*) AS outbox_rows,
  COUNTIF(quarantine_status = 'quarantined') AS quarantined_rows,
  COUNTIF(delivery_status = 'accepted') AS accepted_rows,
  COUNTIF(delivery_status = 'permanent_failure') AS permanent_failure_rows,
  COUNTIF(delivery_status = 'retryable_failure') AS retryable_failure_rows,
  COUNTIF(lease_expires_at > CURRENT_TIMESTAMP()) AS active_lease_rows,
  MAX(updated_at) AS last_updated_at,
  TRUE AS intelligence_safe,
  FALSE AS dashboard_safe,
  FALSE AS activation_safe
FROM `marketing-api-488017.cefa_restricted.parent_conversion_outbox`
GROUP BY
  activity_date,
  platform,
  destination_action_key,
  canonical_stage,
  activation_mode,
  delivery_status,
  quarantine_status;

CREATE OR REPLACE VIEW `marketing-api-488017.mart_cefa_growth_dashboard.dashboard_parent_crm_offline_activation_readiness_latest`
OPTIONS (
  description = 'Redacted parent CRM offline activation readiness. Advisory only; it does not replace existing dashboard KPIs.'
) AS
SELECT
  activity_date,
  platform,
  destination_action_key,
  canonical_stage,
  activation_mode,
  SUM(outbox_rows) AS outbox_rows,
  SUM(quarantined_rows) AS quarantined_rows,
  SUM(accepted_rows) AS accepted_rows,
  SUM(permanent_failure_rows) AS permanent_failure_rows,
  SUM(retryable_failure_rows) AS retryable_failure_rows,
  SUM(active_lease_rows) AS active_lease_rows,
  MAX(last_updated_at) AS last_updated_at,
  TRUE AS intelligence_safe,
  FALSE AS dashboard_safe,
  FALSE AS activation_safe
FROM `marketing-api-488017.mart_cefa_growth_intelligence.v_parent_crm_offline_activation_monitoring_daily`
GROUP BY
  activity_date,
  platform,
  destination_action_key,
  canonical_stage,
  activation_mode;
