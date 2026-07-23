"""Restricted BigQuery persistence for the parent Form 4 identity bridge."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping, Protocol, Sequence

from .bigquery_store import (
    PROJECT_ID,
    RESTRICTED_DATASET,
    assert_no_prohibited_raw_pii,
    bigquery,
)
from .models import require_safe_opaque_id, require_sha256_hex


IDENTITY_INBOX_TABLE = (
    f"{PROJECT_ID}.{RESTRICTED_DATASET}.parent_form4_identity_inbox"
)


class QueryJob(Protocol):
    num_dml_affected_rows: int | None

    def result(self) -> Any: ...


class BigQueryClient(Protocol):
    def query(
        self,
        query: str,
        job_config: bigquery.QueryJobConfig | None = None,
    ) -> QueryJob: ...


def _utc_timestamp(value: datetime | None = None) -> str:
    timestamp = value or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class ParentIdentityBigQueryStore:
    """Idempotent inbox and binder-state boundary."""

    def __init__(
        self,
        client: BigQueryClient | None = None,
        *,
        project_id: str = PROJECT_ID,
    ) -> None:
        self.client = client or bigquery.Client(project=project_id)

    def upsert_identity(self, record: Mapping[str, Any]) -> None:
        assert_no_prohibited_raw_pii(record)
        require_safe_opaque_id(str(record["form4_event_id"]), "form4_event_id")
        require_safe_opaque_id(str(record["form_entry_id"]), "form_entry_id")
        for key, value in record.items():
            if key.endswith("_hmac") and value is not None:
                require_sha256_hex(str(value), key)
        query = f"""
        MERGE `{IDENTITY_INBOX_TABLE}` AS target
        USING (
          SELECT
            @form4_event_id AS form4_event_id,
            @form_entry_id AS form_entry_id,
            @school_uuid AS school_uuid,
            @greenrope_group_id AS greenrope_group_id,
            @submitted_at AS submitted_at,
            @assigned_email_hmac AS assigned_email_hmac,
            @assigned_phone_hmac AS assigned_phone_hmac,
            @parent_first_hmac AS parent_first_hmac,
            @parent_last_hmac AS parent_last_hmac,
            @child_dob_hmac AS child_dob_hmac,
            @program_hmac AS program_hmac,
            @requested_start_hmac AS requested_start_hmac,
            @consent_signal_status AS consent_signal_status,
            @bridge_status AS bridge_status,
            @quarantine_reason AS quarantine_reason,
            @created_at AS created_at,
            @updated_at AS updated_at
        ) AS source
        ON target.form4_event_id = source.form4_event_id
        WHEN NOT MATCHED THEN
          INSERT (
            form4_event_id, form_entry_id, school_uuid, greenrope_group_id,
            submitted_at, assigned_email_hmac, assigned_phone_hmac,
            parent_first_hmac, parent_last_hmac, child_dob_hmac, program_hmac,
            requested_start_hmac, consent_signal_status, bridge_status,
            candidate_count, match_score, opportunity_id_hmac,
            quarantine_reason, greenrope_readback_confirmed, attempt_count,
            last_attempt_at, matched_at, greenrope_written_at, created_at,
            updated_at
          ) VALUES (
            source.form4_event_id, source.form_entry_id, source.school_uuid,
            source.greenrope_group_id, source.submitted_at,
            source.assigned_email_hmac, source.assigned_phone_hmac,
            source.parent_first_hmac, source.parent_last_hmac,
            source.child_dob_hmac, source.program_hmac,
            source.requested_start_hmac, source.consent_signal_status,
            source.bridge_status, 0, NULL, NULL, source.quarantine_reason,
            FALSE, 0, NULL, NULL, NULL, source.created_at, source.updated_at
          )
        WHEN MATCHED
          AND target.greenrope_readback_confirmed = FALSE
          AND target.form_entry_id = source.form_entry_id
        THEN UPDATE SET
          school_uuid = source.school_uuid,
          greenrope_group_id = source.greenrope_group_id,
          submitted_at = source.submitted_at,
          assigned_email_hmac = source.assigned_email_hmac,
          assigned_phone_hmac = source.assigned_phone_hmac,
          parent_first_hmac = source.parent_first_hmac,
          parent_last_hmac = source.parent_last_hmac,
          child_dob_hmac = source.child_dob_hmac,
          program_hmac = source.program_hmac,
          requested_start_hmac = source.requested_start_hmac,
          consent_signal_status = source.consent_signal_status,
          bridge_status = target.bridge_status,
          quarantine_reason = target.quarantine_reason,
          updated_at = source.updated_at
        """
        self._query(query, self._record_parameters(record))

    def pending_identities(self, *, limit: int = 500) -> list[dict[str, Any]]:
        if not 1 <= limit <= 5000:
            raise ValueError("limit must be between 1 and 5000")
        query = f"""
        SELECT
          form4_event_id, form_entry_id, school_uuid, greenrope_group_id,
          submitted_at, assigned_email_hmac, assigned_phone_hmac,
          parent_first_hmac, parent_last_hmac, child_dob_hmac, program_hmac,
          requested_start_hmac, consent_signal_status, bridge_status,
          candidate_count, match_score, opportunity_id_hmac,
          quarantine_reason, attempt_count, created_at, updated_at
        FROM `{IDENTITY_INBOX_TABLE}`
        WHERE greenrope_readback_confirmed = FALSE
          AND bridge_status IN (
            'captured',
            'matched',
            'awaiting_greenrope_fields',
            'retryable_failure'
          )
        ORDER BY submitted_at ASC
        LIMIT @limit
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
            ]
        )
        rows = self.client.query(query, job_config=job_config).result()
        return [dict(row.items()) if hasattr(row, "items") else dict(row) for row in rows]

    def latest_submitted_at(self) -> datetime | None:
        query = f"""
        SELECT MAX(submitted_at) AS latest_submitted_at
        FROM `{IDENTITY_INBOX_TABLE}`
        """
        rows = list(self.client.query(query).result())
        if not rows:
            return None
        row = rows[0]
        value = (
            row.get("latest_submitted_at")
            if isinstance(row, Mapping)
            else row["latest_submitted_at"]
        )
        return value

    def record_match_state(
        self,
        *,
        form4_event_id: str,
        bridge_status: str,
        candidate_count: int,
        match_score: int | None,
        opportunity_id_hmac: str | None,
        quarantine_reason: str | None,
        readback_confirmed: bool = False,
        written_at: datetime | None = None,
    ) -> bool:
        allowed_statuses = {
            "matched",
            "awaiting_greenrope_fields",
            "quarantined",
            "greenrope_confirmed",
            "greenrope_identity_conflict",
            "retryable_failure",
        }
        if bridge_status not in allowed_statuses:
            raise ValueError(f"unsupported bridge status: {bridge_status}")
        if candidate_count < 0:
            raise ValueError("candidate_count cannot be negative")
        if opportunity_id_hmac:
            require_sha256_hex(opportunity_id_hmac, "opportunity_id_hmac")
        query = f"""
        UPDATE `{IDENTITY_INBOX_TABLE}`
        SET
          bridge_status = @bridge_status,
          candidate_count = @candidate_count,
          match_score = @match_score,
          opportunity_id_hmac = @opportunity_id_hmac,
          quarantine_reason = @quarantine_reason,
          greenrope_readback_confirmed = @readback_confirmed,
          attempt_count = attempt_count + 1,
          last_attempt_at = CURRENT_TIMESTAMP(),
          matched_at = IF(
            @opportunity_id_hmac IS NOT NULL,
            COALESCE(matched_at, CURRENT_TIMESTAMP()),
            matched_at
          ),
          greenrope_written_at = COALESCE(@written_at, greenrope_written_at),
          updated_at = CURRENT_TIMESTAMP()
        WHERE form4_event_id = @form4_event_id
          AND greenrope_readback_confirmed = FALSE
        """
        affected = self._query(
            query,
            [
                bigquery.ScalarQueryParameter(
                    "form4_event_id",
                    "STRING",
                    require_safe_opaque_id(form4_event_id, "form4_event_id"),
                ),
                bigquery.ScalarQueryParameter("bridge_status", "STRING", bridge_status),
                bigquery.ScalarQueryParameter(
                    "candidate_count",
                    "INT64",
                    candidate_count,
                ),
                bigquery.ScalarQueryParameter("match_score", "INT64", match_score),
                bigquery.ScalarQueryParameter(
                    "opportunity_id_hmac",
                    "STRING",
                    opportunity_id_hmac,
                ),
                bigquery.ScalarQueryParameter(
                    "quarantine_reason",
                    "STRING",
                    quarantine_reason,
                ),
                bigquery.ScalarQueryParameter(
                    "readback_confirmed",
                    "BOOL",
                    readback_confirmed,
                ),
                bigquery.ScalarQueryParameter(
                    "written_at",
                    "TIMESTAMP",
                    _utc_timestamp(written_at) if written_at else None,
                ),
            ],
        )
        return affected == 1

    def _record_parameters(
        self,
        row: Mapping[str, Any],
    ) -> Sequence[bigquery.ScalarQueryParameter]:
        types = {
            "form4_event_id": "STRING",
            "form_entry_id": "STRING",
            "school_uuid": "STRING",
            "greenrope_group_id": "STRING",
            "submitted_at": "TIMESTAMP",
            "assigned_email_hmac": "STRING",
            "assigned_phone_hmac": "STRING",
            "parent_first_hmac": "STRING",
            "parent_last_hmac": "STRING",
            "child_dob_hmac": "STRING",
            "program_hmac": "STRING",
            "requested_start_hmac": "STRING",
            "consent_signal_status": "STRING",
            "bridge_status": "STRING",
            "quarantine_reason": "STRING",
            "created_at": "TIMESTAMP",
            "updated_at": "TIMESTAMP",
        }
        return [
            bigquery.ScalarQueryParameter(name, type_name, row.get(name))
            for name, type_name in types.items()
        ]

    def _query(
        self,
        query: str,
        parameters: Sequence[bigquery.ScalarQueryParameter],
    ) -> int:
        job_config = bigquery.QueryJobConfig(query_parameters=list(parameters))
        job = self.client.query(query, job_config=job_config)
        job.result()
        return int(job.num_dml_affected_rows or 0)
