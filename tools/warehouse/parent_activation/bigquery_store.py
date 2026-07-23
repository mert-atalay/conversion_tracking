"""Restricted BigQuery persistence for parent CRM offline activation.

Python 3.11+ is required by the package contracts. This module never persists
raw contact data or platform payloads, and every delivery state transition is
owned by one unexpired worker lease.
"""

from __future__ import annotations

import hashlib
import hmac
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol, Sequence

from .models import require_safe_opaque_id, require_sha256_hex

try:
    from google.cloud import bigquery
except ModuleNotFoundError:  # pragma: no cover - supports isolated unit tests.
    class _ScalarQueryParameter:
        def __init__(self, name: str, type_: str, value: Any) -> None:
            self.name = name
            self.type_ = type_
            self.value = value

    class _QueryJobConfig:
        def __init__(self, *, query_parameters: list[Any] | None = None) -> None:
            self.query_parameters = query_parameters or []

    class _BigQueryTestShim:
        ScalarQueryParameter = _ScalarQueryParameter
        QueryJobConfig = _QueryJobConfig

        class Client:
            def __init__(self, *_: Any, **__: Any) -> None:
                raise RuntimeError("google-cloud-bigquery is required when no client is injected")

    bigquery = _BigQueryTestShim()


PROJECT_ID = "marketing-api-488017"
RESTRICTED_DATASET = "cefa_parent_activation_restricted"
OUTBOX_TABLE = f"{PROJECT_ID}.{RESTRICTED_DATASET}.parent_conversion_outbox"
SNAPSHOT_TABLE = f"{PROJECT_ID}.{RESTRICTED_DATASET}.parent_crm_lifecycle_state_snapshot"
LIFECYCLE_TABLE = f"{PROJECT_ID}.{RESTRICTED_DATASET}.parent_crm_lifecycle_event"
DELIVERY_ATTEMPT_TABLE = f"{PROJECT_ID}.{RESTRICTED_DATASET}.parent_conversion_delivery_attempt"

BASELINE_NON_UPLOADABLE = "baseline_non_uploadable"
QUARANTINED = "quarantined"
NOT_QUARANTINED = "not_quarantined"
ACCEPTED = "accepted"

PROHIBITED_RAW_PII_COLUMNS = frozenset(
    {
        "name",
        "first_name",
        "last_name",
        "email",
        "phone",
        "address",
        "dob",
        "date_of_birth",
        "notes",
        "ip_address",
        "raw_payload",
        "payload",
    }
)
PROHIBITED_RUNTIME_MATCH_KEYS = frozenset(
    {"gclid", "gbraid", "wbraid", "fbclid", "fbc", "fbp"}
)
_PROHIBITED_NORMALIZED_KEYS = frozenset(
    re.sub(r"[^a-z0-9]", "", key.lower())
    for key in PROHIBITED_RAW_PII_COLUMNS | PROHIBITED_RUNTIME_MATCH_KEYS
)
_HASH_KEYS = frozenset({"emailsha256", "phonesha256"})
_EMAIL_VALUE_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
_PHONE_VALUE_RE = re.compile(r"(?<!\w)\+?\d[\d\s().-]{6,}\d(?!\w)")
_ISO_TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}(?:(?:T|\s)\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)?$"
)


class QueryJob(Protocol):
    num_dml_affected_rows: int | None

    def result(self) -> Any: ...


class BigQueryClient(Protocol):
    def query(self, query: str, job_config: bigquery.QueryJobConfig | None = None) -> QueryJob: ...

    def insert_rows_json(
        self,
        table: str,
        json_rows: Sequence[Mapping[str, Any]],
    ) -> Sequence[Mapping[str, Any]]: ...


@dataclass(frozen=True)
class OutboxIdentity:
    """The immutable dedupe identity for one platform destination."""

    form4_event_id: str
    canonical_stage: str
    platform: str
    destination_action_key: str


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_timestamp(value: datetime | None = None) -> str:
    timestamp = value or _utc_now()
    if timestamp.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    return timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _require_nonempty(value: str, field: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field} must be non-empty")
    return normalized


def _normalized_key(value: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def _contains_phone_like_value(value: str) -> bool:
    if _ISO_TIMESTAMP_RE.fullmatch(value.strip()):
        return False
    for match in _PHONE_VALUE_RE.finditer(value):
        candidate = match.group(0)
        digits = re.sub(r"\D", "", candidate)
        if 7 <= len(digits) <= 15 and any(marker in candidate for marker in ("+", "(", ")", " ", "-")):
            return True
    return False


def _assert_safe_value(value: Any, path: str) -> None:
    if not isinstance(value, str):
        return
    if _EMAIL_VALUE_RE.search(value) or _contains_phone_like_value(value):
        raise ValueError(f"raw PII-like value is prohibited at {path}")


def assert_no_prohibited_raw_pii(record: Mapping[str, Any]) -> None:
    """Recursively reject normalized PII/match-key aliases and raw values."""

    def walk(value: Any, path: str) -> None:
        if isinstance(value, Mapping):
            for raw_key, nested in value.items():
                key = _normalized_key(raw_key)
                child_path = f"{path}.{raw_key}" if path else str(raw_key)
                if key in _PROHIBITED_NORMALIZED_KEYS:
                    raise ValueError(f"prohibited raw PII field: {child_path}")
                if key in _HASH_KEYS and nested is not None:
                    require_sha256_hex(str(nested), str(raw_key))
                walk(nested, child_path)
            return
        if isinstance(value, (list, tuple, set)):
            for index, nested in enumerate(value):
                walk(nested, f"{path}[{index}]")
            return
        _assert_safe_value(value, path)

    walk(record, "")


def redact_diagnostic_text(value: object | None, *, maximum_length: int = 500) -> str | None:
    """Remove contact-shaped values before platform diagnostics reach logs/BQ."""

    if value is None:
        return None
    text = str(value)
    text = _EMAIL_VALUE_RE.sub("[redacted-email]", text)
    text = _PHONE_VALUE_RE.sub("[redacted-number]", text)
    return text[:maximum_length]


def hmac_hex(secret: bytes, *parts: str) -> str:
    if not secret:
        raise ValueError("transaction secret must be non-empty")
    payload = "|".join(_require_nonempty(part, "identity part") for part in parts)
    return hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()


def transaction_id_for(identity: OutboxIdentity, secret: bytes) -> str:
    """Create one stable transaction ID for event, stage, platform, and action."""

    return hmac_hex(
        secret,
        "cefa_parent_crm_v1",
        require_safe_opaque_id(identity.form4_event_id, "form4_event_id"),
        require_safe_opaque_id(identity.canonical_stage, "canonical_stage"),
        require_safe_opaque_id(identity.platform.lower(), "platform"),
        require_safe_opaque_id(identity.destination_action_key, "destination_action_key"),
    )


def outbox_id_for(transaction_id: str, identity: OutboxIdentity) -> str:
    payload = "|".join(
        (
            "cefa_parent_outbox_v1",
            require_sha256_hex(transaction_id, "transaction_id"),
            require_safe_opaque_id(identity.platform.lower(), "platform"),
            require_safe_opaque_id(identity.destination_action_key, "destination_action_key"),
        )
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ParentActivationBigQueryStore:
    """Persistence boundary for restricted parent lifecycle activation rows."""

    def __init__(
        self,
        client: BigQueryClient | None = None,
        *,
        project_id: str = PROJECT_ID,
        transaction_secret: bytes | None = None,
    ) -> None:
        self.client = client or bigquery.Client(project=project_id)
        self.project_id = project_id
        self.transaction_secret = transaction_secret

    def apply_contract(self, sql_path: Path | None = None) -> None:
        """Apply the additive DDL script. Callers control when this is executed."""

        path = sql_path or Path(__file__).resolve().parents[1] / "parent_crm_lifecycle_foundation.sql"
        job = self.client.query(path.read_text(encoding="utf-8"))
        job.result()

    def write_initial_snapshot(self, rows: Iterable[Mapping[str, Any]]) -> None:
        """Persist baseline state that is permanently ineligible for activation."""

        now = _utc_timestamp()
        prepared: list[dict[str, Any]] = []
        for source_row in rows:
            assert_no_prohibited_raw_pii(source_row)
            row = dict(source_row)
            row["is_initial_baseline"] = True
            row["baseline_status"] = BASELINE_NON_UPLOADABLE
            row["pii_redacted"] = True
            row.setdefault("loaded_at", now)
            prepared.append(row)
        self._insert_rows(SNAPSHOT_TABLE, prepared)

    def write_lifecycle_event(self, event: Mapping[str, Any]) -> None:
        """Persist one lifecycle event, force-blocking every baseline record."""

        assert_no_prohibited_raw_pii(event)
        row = dict(event)
        is_baseline = bool(row.get("is_initial_baseline"))
        if is_baseline:
            row["eligibility_status"] = BASELINE_NON_UPLOADABLE
            row["quarantine_status"] = QUARANTINED
            row["quarantine_reason"] = BASELINE_NON_UPLOADABLE
        else:
            row.setdefault("quarantine_status", NOT_QUARANTINED)
        row.setdefault("created_at", _utc_timestamp())
        self._insert_rows(LIFECYCLE_TABLE, [row])

    def build_outbox_row(
        self,
        *,
        selected_lifecycle_event_id: str,
        identity: OutboxIdentity,
        activation_subject_id_hmac: str,
        activation_identity_scope: str,
        source_lifecycle_event_count: int,
        source_is_initial_baseline: bool,
        school_uuid: str,
        destination_account_id: str,
        platform_event_name: str,
        event_timestamp: datetime,
        match_key_ref: str | None,
        activation_mode: str,
        quarantine_reason: str | None = None,
    ) -> dict[str, Any]:
        """Return a deterministic, adapter-aligned outbox row."""

        if self.transaction_secret is None:
            raise ValueError("transaction_secret is required to build an outbox row")
        if source_lifecycle_event_count < 1:
            raise ValueError("source_lifecycle_event_count must be at least one")
        require_sha256_hex(activation_subject_id_hmac, "activation_subject_id_hmac")
        transaction_id = transaction_id_for(identity, self.transaction_secret)
        now = _utc_timestamp()
        effective_reason = BASELINE_NON_UPLOADABLE if source_is_initial_baseline else quarantine_reason
        is_quarantined = bool(effective_reason)
        return {
            "outbox_id": outbox_id_for(transaction_id, identity),
            "selected_lifecycle_event_id": require_safe_opaque_id(
                selected_lifecycle_event_id,
                "selected_lifecycle_event_id",
            ),
            "form4_event_id": require_safe_opaque_id(identity.form4_event_id, "form4_event_id"),
            "activation_subject_id_hmac": activation_subject_id_hmac,
            "activation_identity_scope": require_safe_opaque_id(
                activation_identity_scope,
                "activation_identity_scope",
            ),
            "canonical_stage": require_safe_opaque_id(identity.canonical_stage, "canonical_stage"),
            "source_lifecycle_event_count": source_lifecycle_event_count,
            "source_is_initial_baseline": source_is_initial_baseline,
            "school_uuid": require_safe_opaque_id(school_uuid, "school_uuid"),
            "platform": require_safe_opaque_id(identity.platform.lower(), "platform"),
            "destination_account_id": require_safe_opaque_id(
                destination_account_id,
                "destination_account_id",
            ),
            "destination_action_key": require_safe_opaque_id(
                identity.destination_action_key,
                "destination_action_key",
            ),
            "platform_event_name": _require_nonempty(platform_event_name, "platform_event_name"),
            "transaction_id": transaction_id,
            "event_timestamp": _utc_timestamp(event_timestamp),
            "event_value": None,
            "currency": None,
            "match_key_ref": (
                require_safe_opaque_id(match_key_ref, "match_key_ref")
                if match_key_ref
                else None
            ),
            "activation_mode": require_safe_opaque_id(activation_mode, "activation_mode"),
            "delivery_status": "blocked" if is_quarantined else "queued",
            "quarantine_status": QUARANTINED if is_quarantined else NOT_QUARANTINED,
            "quarantine_reason": effective_reason,
            "attempt_count": 0,
            "next_attempt_at": None if is_quarantined else now,
            "lease_owner": None,
            "lease_expires_at": None,
            "accepted_at": None,
            "accepted_lock_id": None,
            "last_error_code": None,
            "last_error_message": None,
            "created_at": now,
            "updated_at": now,
        }

    def enqueue_outbox(self, row: Mapping[str, Any]) -> None:
        """Merge an outbox row without reopening baseline, leased, or final rows."""

        assert_no_prohibited_raw_pii(row)
        if bool(row.get("source_is_initial_baseline")):
            if (
                row.get("delivery_status") != "blocked"
                or row.get("quarantine_reason") != BASELINE_NON_UPLOADABLE
            ):
                raise ValueError("baseline outbox rows must remain blocked")
        required = (
            "outbox_id",
            "form4_event_id",
            "canonical_stage",
            "platform",
            "destination_action_key",
            "transaction_id",
            "school_uuid",
            "event_timestamp",
        )
        for field in required:
            _require_nonempty(str(row.get(field, "")), field)
        query = f"""
        MERGE `{OUTBOX_TABLE}` AS target
        USING (
          SELECT
            @outbox_id AS outbox_id,
            @selected_lifecycle_event_id AS selected_lifecycle_event_id,
            @form4_event_id AS form4_event_id,
            @activation_subject_id_hmac AS activation_subject_id_hmac,
            @activation_identity_scope AS activation_identity_scope,
            @canonical_stage AS canonical_stage,
            @source_lifecycle_event_count AS source_lifecycle_event_count,
            @source_is_initial_baseline AS source_is_initial_baseline,
            @school_uuid AS school_uuid,
            @platform AS platform,
            @destination_account_id AS destination_account_id,
            @destination_action_key AS destination_action_key,
            @platform_event_name AS platform_event_name,
            @transaction_id AS transaction_id,
            @event_timestamp AS event_timestamp,
            @match_key_ref AS match_key_ref,
            @activation_mode AS activation_mode,
            @delivery_status AS delivery_status,
            @quarantine_status AS quarantine_status,
            @quarantine_reason AS quarantine_reason,
            @next_attempt_at AS next_attempt_at,
            @created_at AS created_at,
            @updated_at AS updated_at
        ) AS source
        ON target.form4_event_id = source.form4_event_id
          AND target.canonical_stage = source.canonical_stage
          AND target.platform = source.platform
          AND target.destination_action_key = source.destination_action_key
        WHEN NOT MATCHED THEN
          INSERT (
            outbox_id, selected_lifecycle_event_id, form4_event_id,
            activation_subject_id_hmac, activation_identity_scope, canonical_stage,
            source_lifecycle_event_count, source_is_initial_baseline, school_uuid,
            platform, destination_account_id, destination_action_key,
            platform_event_name, transaction_id, event_timestamp, event_value,
            currency, match_key_ref, activation_mode, delivery_status,
            quarantine_status, quarantine_reason, attempt_count, next_attempt_at,
            lease_owner, lease_expires_at, accepted_at, accepted_lock_id,
            last_error_code, last_error_message, created_at, updated_at
          ) VALUES (
            source.outbox_id, source.selected_lifecycle_event_id, source.form4_event_id,
            source.activation_subject_id_hmac, source.activation_identity_scope,
            source.canonical_stage, source.source_lifecycle_event_count,
            source.source_is_initial_baseline, source.school_uuid, source.platform,
            source.destination_account_id, source.destination_action_key,
            source.platform_event_name, source.transaction_id, source.event_timestamp,
            NULL, NULL, source.match_key_ref, source.activation_mode,
            source.delivery_status, source.quarantine_status, source.quarantine_reason,
            0, source.next_attempt_at, NULL, NULL, NULL, NULL, NULL, NULL,
            source.created_at, source.updated_at
          )
        WHEN MATCHED
          AND target.accepted_at IS NULL
          AND target.delivery_status NOT IN ('leased', 'permanent_failure')
        THEN UPDATE SET
          updated_at = source.updated_at,
          selected_lifecycle_event_id = source.selected_lifecycle_event_id,
          source_lifecycle_event_count = source.source_lifecycle_event_count,
          source_is_initial_baseline = source.source_is_initial_baseline,
          school_uuid = source.school_uuid,
          match_key_ref = source.match_key_ref,
          activation_mode = source.activation_mode,
          delivery_status = source.delivery_status,
          quarantine_status = source.quarantine_status,
          quarantine_reason = source.quarantine_reason,
          next_attempt_at = source.next_attempt_at
        """
        self._query(query, self._outbox_parameters(row))

    def lease_outbox(self, outbox_id: str, worker_id: str, lease_seconds: int = 300) -> bool:
        """Atomically lease one eligible row and report whether ownership won."""

        if lease_seconds < 1:
            raise ValueError("lease_seconds must be positive")
        query = f"""
        UPDATE `{OUTBOX_TABLE}`
        SET
          delivery_status = 'leased',
          lease_owner = @worker_id,
          lease_expires_at = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL @lease_seconds SECOND),
          attempt_count = attempt_count + 1,
          updated_at = CURRENT_TIMESTAMP()
        WHERE outbox_id = @outbox_id
          AND source_is_initial_baseline = FALSE
          AND accepted_at IS NULL
          AND quarantine_status = '{NOT_QUARANTINED}'
          AND delivery_status IN ('queued', 'retryable_failure', 'validate_only_pass', 'test_accepted')
          AND (lease_expires_at IS NULL OR lease_expires_at <= CURRENT_TIMESTAMP())
          AND (next_attempt_at IS NULL OR next_attempt_at <= CURRENT_TIMESTAMP())
        """
        affected = self._query(
            query,
            [
                bigquery.ScalarQueryParameter("outbox_id", "STRING", outbox_id),
                bigquery.ScalarQueryParameter("worker_id", "STRING", worker_id),
                bigquery.ScalarQueryParameter("lease_seconds", "INT64", lease_seconds),
            ],
        )
        return affected == 1

    def record_delivery_attempt(self, attempt: Mapping[str, Any]) -> None:
        """Append redacted diagnostics only; platform payloads are never retained."""

        row = dict(attempt)
        for key in ("error_message", "warning_message", "diagnostic_message"):
            if key in row:
                row[key] = redact_diagnostic_text(row[key])
        assert_no_prohibited_raw_pii(row)
        self._insert_rows(DELIVERY_ATTEMPT_TABLE, [row])

    def mark_accepted(self, outbox_id: str, worker_id: str, accepted_lock_id: str) -> bool:
        """Accept exactly once, and only for the current unexpired lease owner."""

        query = f"""
        UPDATE `{OUTBOX_TABLE}`
        SET
          delivery_status = '{ACCEPTED}',
          accepted_at = CURRENT_TIMESTAMP(),
          accepted_lock_id = @accepted_lock_id,
          lease_owner = NULL,
          lease_expires_at = NULL,
          next_attempt_at = NULL,
          last_error_code = NULL,
          last_error_message = NULL,
          updated_at = CURRENT_TIMESTAMP()
        WHERE outbox_id = @outbox_id
          AND source_is_initial_baseline = FALSE
          AND accepted_at IS NULL
          AND quarantine_status = '{NOT_QUARANTINED}'
          AND delivery_status = 'leased'
          AND lease_owner = @worker_id
          AND lease_expires_at > CURRENT_TIMESTAMP()
        """
        return self._leased_transition(
            query,
            outbox_id,
            worker_id,
            [
                bigquery.ScalarQueryParameter(
                    "accepted_lock_id",
                    "STRING",
                    require_safe_opaque_id(accepted_lock_id, "accepted_lock_id"),
                )
            ],
        )

    def release_lease(self, outbox_id: str, worker_id: str) -> bool:
        """Release a current lease back to the queue without changing attempts."""

        query = f"""
        UPDATE `{OUTBOX_TABLE}`
        SET
          delivery_status = 'queued',
          lease_owner = NULL,
          lease_expires_at = NULL,
          next_attempt_at = CURRENT_TIMESTAMP(),
          updated_at = CURRENT_TIMESTAMP()
        WHERE outbox_id = @outbox_id
          AND delivery_status = 'leased'
          AND lease_owner = @worker_id
          AND lease_expires_at > CURRENT_TIMESTAMP()
          AND accepted_at IS NULL
        """
        return self._leased_transition(query, outbox_id, worker_id)

    def mark_retryable_failure(
        self,
        outbox_id: str,
        worker_id: str,
        *,
        error_code: str,
        error_message: str | None,
        next_attempt_at: datetime,
    ) -> bool:
        """Release a lease into a scheduled, redacted retry state."""

        query = f"""
        UPDATE `{OUTBOX_TABLE}`
        SET
          delivery_status = 'retryable_failure',
          lease_owner = NULL,
          lease_expires_at = NULL,
          next_attempt_at = @next_attempt_at,
          last_error_code = @error_code,
          last_error_message = @error_message,
          updated_at = CURRENT_TIMESTAMP()
        WHERE outbox_id = @outbox_id
          AND delivery_status = 'leased'
          AND lease_owner = @worker_id
          AND lease_expires_at > CURRENT_TIMESTAMP()
          AND accepted_at IS NULL
        """
        return self._leased_transition(
            query,
            outbox_id,
            worker_id,
            [
                bigquery.ScalarQueryParameter(
                    "error_code",
                    "STRING",
                    require_safe_opaque_id(error_code, "error_code"),
                ),
                bigquery.ScalarQueryParameter(
                    "error_message",
                    "STRING",
                    redact_diagnostic_text(error_message),
                ),
                bigquery.ScalarQueryParameter(
                    "next_attempt_at",
                    "TIMESTAMP",
                    _utc_timestamp(next_attempt_at),
                ),
            ],
        )

    def mark_permanent_failure(
        self,
        outbox_id: str,
        worker_id: str,
        *,
        error_code: str,
        error_message: str | None,
    ) -> bool:
        """End a leased row in a redacted, non-retryable failure state."""

        query = f"""
        UPDATE `{OUTBOX_TABLE}`
        SET
          delivery_status = 'permanent_failure',
          lease_owner = NULL,
          lease_expires_at = NULL,
          next_attempt_at = NULL,
          last_error_code = @error_code,
          last_error_message = @error_message,
          updated_at = CURRENT_TIMESTAMP()
        WHERE outbox_id = @outbox_id
          AND delivery_status = 'leased'
          AND lease_owner = @worker_id
          AND lease_expires_at > CURRENT_TIMESTAMP()
          AND accepted_at IS NULL
        """
        return self._leased_transition(
            query,
            outbox_id,
            worker_id,
            [
                bigquery.ScalarQueryParameter(
                    "error_code",
                    "STRING",
                    require_safe_opaque_id(error_code, "error_code"),
                ),
                bigquery.ScalarQueryParameter(
                    "error_message",
                    "STRING",
                    redact_diagnostic_text(error_message),
                ),
            ],
        )

    def _leased_transition(
        self,
        query: str,
        outbox_id: str,
        worker_id: str,
        extra_parameters: Sequence[bigquery.ScalarQueryParameter] = (),
    ) -> bool:
        parameters = [
            bigquery.ScalarQueryParameter("outbox_id", "STRING", outbox_id),
            bigquery.ScalarQueryParameter("worker_id", "STRING", worker_id),
            *extra_parameters,
        ]
        return self._query(query, parameters) == 1

    def _outbox_parameters(self, row: Mapping[str, Any]) -> list[bigquery.ScalarQueryParameter]:
        parameter_types = {
            "outbox_id": "STRING",
            "selected_lifecycle_event_id": "STRING",
            "form4_event_id": "STRING",
            "activation_subject_id_hmac": "STRING",
            "activation_identity_scope": "STRING",
            "canonical_stage": "STRING",
            "source_lifecycle_event_count": "INT64",
            "source_is_initial_baseline": "BOOL",
            "school_uuid": "STRING",
            "platform": "STRING",
            "destination_account_id": "STRING",
            "destination_action_key": "STRING",
            "platform_event_name": "STRING",
            "transaction_id": "STRING",
            "event_timestamp": "TIMESTAMP",
            "match_key_ref": "STRING",
            "activation_mode": "STRING",
            "delivery_status": "STRING",
            "quarantine_status": "STRING",
            "quarantine_reason": "STRING",
            "next_attempt_at": "TIMESTAMP",
            "created_at": "TIMESTAMP",
            "updated_at": "TIMESTAMP",
        }
        return [
            bigquery.ScalarQueryParameter(name, type_name, row.get(name))
            for name, type_name in parameter_types.items()
        ]

    def _insert_rows(self, table: str, rows: Sequence[Mapping[str, Any]]) -> None:
        if not rows:
            return
        errors = self.client.insert_rows_json(table, rows)
        if errors:
            raise RuntimeError(f"BigQuery insert failed for {table}: {len(errors)} redacted error(s)")

    def _query(
        self,
        query: str,
        parameters: Sequence[bigquery.ScalarQueryParameter],
    ) -> int:
        job_config = bigquery.QueryJobConfig(query_parameters=list(parameters))
        job = self.client.query(query, job_config=job_config)
        job.result()
        return int(job.num_dml_affected_rows or 0)
