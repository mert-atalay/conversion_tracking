"""Match Form 4 identity inbox rows to GreenRope and write exact IDs safely."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from .greenrope_adapter import GreenRopeClient, evaluate_required_fields
from .greenrope_identity_writer import GreenRopeIdentityWriter
from .identity_bridge import (
    GreenRopeIdentityCandidate,
    parse_greenrope_candidate,
    select_identity_match,
)
from .identity_store import ParentIdentityBigQueryStore


@dataclass(frozen=True, slots=True)
class BinderRunResult:
    field_contract_ready: bool
    write_enabled: bool
    inbox_rows: int
    matched: int
    awaiting_fields: int
    confirmed: int
    quarantined: int
    conflicts: int
    retryable_failures: int
    group_errors: int

    def to_dict(self) -> dict[str, object]:
        return {
            "field_contract_ready": self.field_contract_ready,
            "write_enabled": self.write_enabled,
            "inbox_rows": self.inbox_rows,
            "matched": self.matched,
            "awaiting_fields": self.awaiting_fields,
            "confirmed": self.confirmed,
            "quarantined": self.quarantined,
            "conflicts": self.conflicts,
            "retryable_failures": self.retryable_failures,
            "group_errors": self.group_errors,
        }


def _identity_conflicts(
    candidate: GreenRopeIdentityCandidate,
    identity: Mapping[str, Any],
) -> bool:
    event_id = str(identity["form4_event_id"])
    entry_id = str(identity["form_entry_id"])
    return bool(
        candidate.current_event_id
        and candidate.current_event_id != event_id
        or candidate.current_form_entry_id
        and candidate.current_form_entry_id != entry_id
    )


def _already_confirmed(
    candidate: GreenRopeIdentityCandidate,
    identity: Mapping[str, Any],
) -> bool:
    return (
        candidate.current_event_id == str(identity["form4_event_id"])
        and candidate.current_form_entry_id == str(identity["form_entry_id"])
    )


def run_identity_binder(
    *,
    store: ParentIdentityBigQueryStore,
    client: GreenRopeClient,
    hmac_secret: bytes,
    write_enabled: bool,
    limit: int = 500,
) -> BinderRunResult:
    rows = store.pending_identities(limit=limit)
    field_readiness = evaluate_required_fields(
        field.normalized_label for field in client.opportunity_fields()
    )
    group_ids = sorted(
        {
            str(row.get("greenrope_group_id") or "")
            for row in rows
            if row.get("greenrope_group_id")
        }
    )
    by_group: dict[str, list[GreenRopeIdentityCandidate]] = {}
    group_errors = 0
    for group_id in group_ids:
        candidates: list[GreenRopeIdentityCandidate] = []
        try:
            for raw in client.opportunities(group_id):
                try:
                    candidates.append(
                        parse_greenrope_candidate(
                            raw,
                            group_id=group_id,
                            secret=hmac_secret,
                        )
                    )
                except (KeyError, TypeError, ValueError):
                    continue
            by_group[group_id] = candidates
        except RuntimeError:
            group_errors += 1
    writer = GreenRopeIdentityWriter(client, hmac_secret=hmac_secret)
    counts = {
        "matched": 0,
        "awaiting_fields": 0,
        "confirmed": 0,
        "quarantined": 0,
        "conflicts": 0,
        "retryable_failures": 0,
    }
    now = datetime.now(timezone.utc)
    for identity in rows:
        group_id = str(identity.get("greenrope_group_id") or "")
        if group_id not in by_group:
            store.record_match_state(
                form4_event_id=str(identity["form4_event_id"]),
                bridge_status="retryable_failure",
                candidate_count=0,
                match_score=None,
                opportunity_id_hmac=None,
                quarantine_reason="greenrope_group_fetch_failed",
            )
            counts["retryable_failures"] += 1
            continue
        decision = select_identity_match(identity, by_group[group_id])
        if decision.candidate is None:
            store.record_match_state(
                form4_event_id=str(identity["form4_event_id"]),
                bridge_status="quarantined",
                candidate_count=decision.candidate_count,
                match_score=decision.match_score,
                opportunity_id_hmac=None,
                quarantine_reason=decision.reason,
            )
            counts["quarantined"] += 1
            continue
        candidate = decision.candidate
        if _identity_conflicts(candidate, identity):
            store.record_match_state(
                form4_event_id=str(identity["form4_event_id"]),
                bridge_status="greenrope_identity_conflict",
                candidate_count=decision.candidate_count,
                match_score=decision.match_score,
                opportunity_id_hmac=candidate.opportunity_id_hmac,
                quarantine_reason="greenrope_identity_conflict",
            )
            counts["conflicts"] += 1
            continue
        if _already_confirmed(candidate, identity):
            store.record_match_state(
                form4_event_id=str(identity["form4_event_id"]),
                bridge_status="greenrope_confirmed",
                candidate_count=decision.candidate_count,
                match_score=decision.match_score,
                opportunity_id_hmac=candidate.opportunity_id_hmac,
                quarantine_reason=None,
                readback_confirmed=True,
            )
            counts["confirmed"] += 1
            continue
        if not field_readiness.status == "ready":
            store.record_match_state(
                form4_event_id=str(identity["form4_event_id"]),
                bridge_status="awaiting_greenrope_fields",
                candidate_count=decision.candidate_count,
                match_score=decision.match_score,
                opportunity_id_hmac=candidate.opportunity_id_hmac,
                quarantine_reason="missing_greenrope_identity_fields",
            )
            counts["awaiting_fields"] += 1
            continue
        if not write_enabled:
            store.record_match_state(
                form4_event_id=str(identity["form4_event_id"]),
                bridge_status="matched",
                candidate_count=decision.candidate_count,
                match_score=decision.match_score,
                opportunity_id_hmac=candidate.opportunity_id_hmac,
                quarantine_reason="greenrope_identity_write_disabled",
            )
            counts["matched"] += 1
            continue
        try:
            result = writer.write_and_confirm(
                candidate=candidate,
                event_id=str(identity["form4_event_id"]),
                form_entry_id=str(identity["form_entry_id"]),
            )
        except (RuntimeError, ValueError):
            result = None
        if result and result.request_succeeded and result.readback_confirmed:
            store.record_match_state(
                form4_event_id=str(identity["form4_event_id"]),
                bridge_status="greenrope_confirmed",
                candidate_count=decision.candidate_count,
                match_score=decision.match_score,
                opportunity_id_hmac=candidate.opportunity_id_hmac,
                quarantine_reason=None,
                readback_confirmed=True,
                written_at=now,
            )
            counts["confirmed"] += 1
        else:
            store.record_match_state(
                form4_event_id=str(identity["form4_event_id"]),
                bridge_status="retryable_failure",
                candidate_count=decision.candidate_count,
                match_score=decision.match_score,
                opportunity_id_hmac=candidate.opportunity_id_hmac,
                quarantine_reason="greenrope_write_or_readback_failed",
            )
            counts["retryable_failures"] += 1
    return BinderRunResult(
        field_contract_ready=field_readiness.status == "ready",
        write_enabled=write_enabled,
        inbox_rows=len(rows),
        matched=counts["matched"],
        awaiting_fields=counts["awaiting_fields"],
        confirmed=counts["confirmed"],
        quarantined=counts["quarantined"],
        conflicts=counts["conflicts"],
        retryable_failures=counts["retryable_failures"],
        group_errors=group_errors,
    )
