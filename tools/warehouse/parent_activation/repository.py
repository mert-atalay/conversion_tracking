"""BigQuery read/write boundary for the parent CRM activation runtime.

Only this module may join the restricted Form 4 click evidence to GreenRope
identity. Callers receive bounded, purpose-specific records rather than raw
source rows.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence

from .bigquery_store import (
    LIFECYCLE_TABLE,
    OUTBOX_TABLE,
    PROJECT_ID,
    RESTRICTED_DATASET,
    SNAPSHOT_TABLE,
    assert_no_prohibited_raw_pii,
    bigquery,
)
from .models import Form4Identity, require_safe_opaque_id, require_sha256_hex


MATCH_KEY_TABLE = f"{PROJECT_ID}.{RESTRICTED_DATASET}.parent_crm_match_key"
DELIVERY_ATTEMPT_TABLE = (
    f"{PROJECT_ID}.{RESTRICTED_DATASET}.parent_conversion_delivery_attempt"
)
FORM4_EVENT_TABLE = f"{PROJECT_ID}.raw_website_forms.website_form_submission_events"
FORM4_COLLECTOR_TABLE = f"{PROJECT_ID}.raw_website_forms.form4_event_audit"


@dataclass(frozen=True, slots=True)
class Form4Match:
    identity: Form4Identity
    school_uuid: str | None
    submitted_at: datetime | None
    is_test: bool
    gclid: str | None
    gbraid: str | None
    wbraid: str | None


def _as_utc(value: object | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _row_dict(row: object) -> dict[str, Any]:
    if isinstance(row, Mapping):
        return dict(row)
    return dict(row.items())


class ParentActivationRepository:
    """Restricted source reconciliation and runtime query operations."""

    def __init__(
        self,
        client: bigquery.Client | None = None,
        *,
        project_id: str = PROJECT_ID,
    ) -> None:
        self.client = client or bigquery.Client(project=project_id)

    def baseline_exists(self) -> bool:
        rows = self._query_rows(
            f"""
            SELECT COUNTIF(is_initial_baseline) > 0 AS baseline_exists
            FROM `{SNAPSHOT_TABLE}`
            """
        )
        return bool(rows and rows[0].get("baseline_exists"))

    def latest_states(self) -> dict[str, dict[str, Any]]:
        rows = self._query_rows(
            f"""
            SELECT
              opportunity_id_hmac,
              raw_phase,
              form4_event_id,
              form_entry_id,
              school_uuid,
              snapshot_at,
              is_initial_baseline
            FROM `{SNAPSHOT_TABLE}`
            QUALIFY ROW_NUMBER() OVER (
              PARTITION BY opportunity_id_hmac
              ORDER BY snapshot_at DESC, loaded_at DESC
            ) = 1
            """
        )
        return {
            str(row["opportunity_id_hmac"]): row
            for row in rows
            if row.get("opportunity_id_hmac")
        }

    def insert_state_snapshots(self, rows: Sequence[Mapping[str, Any]]) -> None:
        prepared: list[dict[str, Any]] = []
        for source in rows:
            assert_no_prohibited_raw_pii(source)
            prepared.append(dict(source))
        if not prepared:
            return
        errors = self.client.insert_rows_json(SNAPSHOT_TABLE, prepared)
        if errors:
            raise RuntimeError(
                f"BigQuery insert failed for lifecycle snapshots: {len(errors)} redacted error(s)"
            )

    def insert_lifecycle_events(self, rows: Sequence[Mapping[str, Any]]) -> None:
        prepared: list[dict[str, Any]] = []
        for source in rows:
            assert_no_prohibited_raw_pii(source)
            prepared.append(dict(source))
        if not prepared:
            return
        errors = self.client.insert_rows_json(LIFECYCLE_TABLE, prepared)
        if errors:
            raise RuntimeError(
                f"BigQuery insert failed for lifecycle events: {len(errors)} redacted error(s)"
            )

    def resolve_form4_matches(
        self,
        event_ids: Iterable[str],
        crm_entry_ids: Mapping[str, str | None],
    ) -> dict[str, Form4Match]:
        normalized_ids = sorted(
            {
                require_safe_opaque_id(event_id, "form4_event_id")
                for event_id in event_ids
                if event_id
            }
        )
        if not normalized_ids:
            return {}
        rows = self._query_rows(
            f"""
            WITH collector AS (
              SELECT
                event_id,
                ARRAY_AGG(gclid IGNORE NULLS ORDER BY received_at LIMIT 1)[SAFE_OFFSET(0)] AS gclid,
                ARRAY_AGG(gbraid IGNORE NULLS ORDER BY received_at LIMIT 1)[SAFE_OFFSET(0)] AS gbraid,
                ARRAY_AGG(wbraid IGNORE NULLS ORDER BY received_at LIMIT 1)[SAFE_OFFSET(0)] AS wbraid
              FROM `{FORM4_COLLECTOR_TABLE}`
              WHERE event_id IN UNNEST(@event_ids)
                AND collector_status = 'accepted'
                AND signature_status = 'valid'
              GROUP BY event_id
            )
            SELECT
              forms.event_id,
              CAST(forms.entry_id AS STRING) AS entry_id,
              forms.selected_school_uuid AS school_uuid,
              forms.submitted_at,
              COALESCE(forms.is_test_submission, FALSE) AS is_test,
              collector.gclid,
              collector.gbraid,
              collector.wbraid
            FROM `{FORM4_EVENT_TABLE}` AS forms
            LEFT JOIN collector USING (event_id)
            WHERE forms.form_id = 4
              AND forms.event_id IN UNNEST(@event_ids)
            ORDER BY forms.event_id, forms.entry_id
            """,
            [
                bigquery.ArrayQueryParameter(
                    "event_ids",
                    "STRING",
                    normalized_ids,
                )
            ],
        )
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[str(row["event_id"])].append(row)

        resolved: dict[str, Form4Match] = {}
        for event_id in normalized_ids:
            matches = grouped.get(event_id, [])
            matched_entry_id = str(matches[0]["entry_id"]) if len(matches) == 1 else None
            identity = Form4Identity(
                event_id=event_id,
                form_entry_id=crm_entry_ids.get(event_id),
                matched_event_id=event_id if matches else None,
                matched_form_entry_id=matched_entry_id,
                match_count=len(matches),
            )
            row = matches[0] if len(matches) == 1 else {}
            resolved[event_id] = Form4Match(
                identity=identity,
                school_uuid=str(row["school_uuid"]) if row.get("school_uuid") else None,
                submitted_at=_as_utc(row.get("submitted_at")),
                is_test=bool(row.get("is_test")),
                gclid=str(row["gclid"]) if row.get("gclid") else None,
                gbraid=str(row["gbraid"]) if row.get("gbraid") else None,
                wbraid=str(row["wbraid"]) if row.get("wbraid") else None,
            )
        return resolved

    def upsert_match_key(self, row: Mapping[str, Any]) -> None:
        safe_hash_fields = ("email_sha256", "phone_sha256")
        for field in safe_hash_fields:
            if row.get(field):
                require_sha256_hex(str(row[field]), field)
        require_safe_opaque_id(str(row["form4_event_id"]), "form4_event_id")
        query = f"""
        MERGE `{MATCH_KEY_TABLE}` AS target
        USING (
          SELECT
            @captured_date AS captured_date,
            @form4_event_id AS form4_event_id,
            @opportunity_id_hmac AS opportunity_id_hmac,
            @governed_lead_id_hmac AS governed_lead_id_hmac,
            @email_sha256 AS email_sha256,
            @phone_sha256 AS phone_sha256,
            @gclid AS gclid,
            @gbraid AS gbraid,
            @wbraid AS wbraid,
            @fbc AS fbc,
            @fbp AS fbp,
            @click_id_captured_at AS click_id_captured_at,
            @user_data_captured_at AS user_data_captured_at,
            @match_key_source AS match_key_source,
            @consent_status AS consent_status,
            @expires_at AS expires_at,
            @loaded_at AS loaded_at
        ) AS source
        ON target.form4_event_id = source.form4_event_id
        WHEN NOT MATCHED THEN
          INSERT ROW
        WHEN MATCHED THEN UPDATE SET
          opportunity_id_hmac = COALESCE(source.opportunity_id_hmac, target.opportunity_id_hmac),
          governed_lead_id_hmac = COALESCE(source.governed_lead_id_hmac, target.governed_lead_id_hmac),
          email_sha256 = COALESCE(source.email_sha256, target.email_sha256),
          phone_sha256 = COALESCE(source.phone_sha256, target.phone_sha256),
          gclid = COALESCE(source.gclid, target.gclid),
          gbraid = COALESCE(source.gbraid, target.gbraid),
          wbraid = COALESCE(source.wbraid, target.wbraid),
          fbc = COALESCE(source.fbc, target.fbc),
          fbp = COALESCE(source.fbp, target.fbp),
          click_id_captured_at = COALESCE(source.click_id_captured_at, target.click_id_captured_at),
          user_data_captured_at = COALESCE(source.user_data_captured_at, target.user_data_captured_at),
          consent_status = source.consent_status,
          expires_at = GREATEST(source.expires_at, target.expires_at),
          loaded_at = source.loaded_at
        """
        parameters = [
            bigquery.ScalarQueryParameter("captured_date", "DATE", row.get("captured_date")),
            bigquery.ScalarQueryParameter("form4_event_id", "STRING", row.get("form4_event_id")),
            bigquery.ScalarQueryParameter(
                "opportunity_id_hmac",
                "STRING",
                row.get("opportunity_id_hmac"),
            ),
            bigquery.ScalarQueryParameter(
                "governed_lead_id_hmac",
                "STRING",
                row.get("governed_lead_id_hmac"),
            ),
            bigquery.ScalarQueryParameter("email_sha256", "STRING", row.get("email_sha256")),
            bigquery.ScalarQueryParameter("phone_sha256", "STRING", row.get("phone_sha256")),
            bigquery.ScalarQueryParameter("gclid", "STRING", row.get("gclid")),
            bigquery.ScalarQueryParameter("gbraid", "STRING", row.get("gbraid")),
            bigquery.ScalarQueryParameter("wbraid", "STRING", row.get("wbraid")),
            bigquery.ScalarQueryParameter("fbc", "STRING", row.get("fbc")),
            bigquery.ScalarQueryParameter("fbp", "STRING", row.get("fbp")),
            bigquery.ScalarQueryParameter(
                "click_id_captured_at",
                "TIMESTAMP",
                row.get("click_id_captured_at"),
            ),
            bigquery.ScalarQueryParameter(
                "user_data_captured_at",
                "TIMESTAMP",
                row.get("user_data_captured_at"),
            ),
            bigquery.ScalarQueryParameter(
                "match_key_source",
                "STRING",
                row.get("match_key_source"),
            ),
            bigquery.ScalarQueryParameter(
                "consent_status",
                "STRING",
                row.get("consent_status"),
            ),
            bigquery.ScalarQueryParameter("expires_at", "TIMESTAMP", row.get("expires_at")),
            bigquery.ScalarQueryParameter("loaded_at", "TIMESTAMP", row.get("loaded_at")),
        ]
        self._execute(query, parameters)

    def due_outbox_rows(self, *, limit: int = 100) -> list[dict[str, Any]]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        return self._query_rows(
            f"""
            SELECT *
            FROM `{OUTBOX_TABLE}`
            WHERE source_is_initial_baseline = FALSE
              AND accepted_at IS NULL
              AND quarantine_status = 'not_quarantined'
              AND delivery_status IN ('queued', 'retryable_failure')
              AND (lease_expires_at IS NULL OR lease_expires_at <= CURRENT_TIMESTAMP())
              AND (next_attempt_at IS NULL OR next_attempt_at <= CURRENT_TIMESTAMP())
            ORDER BY event_timestamp, outbox_id
            LIMIT {limit}
            """
        )

    def match_key(self, form4_event_id: str) -> dict[str, Any] | None:
        rows = self._query_rows(
            f"""
            SELECT *
            FROM `{MATCH_KEY_TABLE}`
            WHERE form4_event_id = @form4_event_id
              AND expires_at > CURRENT_TIMESTAMP()
            ORDER BY loaded_at DESC
            LIMIT 1
            """,
            [
                bigquery.ScalarQueryParameter(
                    "form4_event_id",
                    "STRING",
                    require_safe_opaque_id(form4_event_id, "form4_event_id"),
                )
            ],
        )
        return rows[0] if rows else None

    def processing_google_rows(self, *, limit: int = 100) -> list[dict[str, Any]]:
        return self._query_rows(
            f"""
            SELECT
              outbox.*,
              attempt.request_id
            FROM `{OUTBOX_TABLE}` AS outbox
            JOIN `{DELIVERY_ATTEMPT_TABLE}` AS attempt
              USING (outbox_id, transaction_id, platform, destination_action_key)
            WHERE outbox.platform = 'google'
              AND outbox.delivery_status = 'processing'
              AND outbox.accepted_at IS NULL
              AND attempt.request_id IS NOT NULL
            QUALIFY ROW_NUMBER() OVER (
              PARTITION BY outbox.outbox_id
              ORDER BY attempt.attempt_started_at DESC
            ) = 1
            ORDER BY outbox.event_timestamp
            LIMIT {int(limit)}
            """
        )

    def _query_rows(
        self,
        query: str,
        parameters: Sequence[bigquery.QueryParameter] = (),
    ) -> list[dict[str, Any]]:
        config = bigquery.QueryJobConfig(query_parameters=list(parameters))
        result = self.client.query(query, job_config=config).result()
        return [_row_dict(row) for row in result]

    def _execute(
        self,
        query: str,
        parameters: Sequence[bigquery.QueryParameter] = (),
    ) -> int:
        config = bigquery.QueryJobConfig(query_parameters=list(parameters))
        job = self.client.query(query, job_config=config)
        job.result()
        return int(job.num_dml_affected_rows or 0)
