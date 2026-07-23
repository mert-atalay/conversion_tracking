"""PII-safe data contracts for the offline activation core.

These contracts intentionally accept only opaque/HMAC identifiers and resolved
Form 4 identity. Raw contact data and raw CRM payloads must stay out of these
objects and out of the durable lifecycle ledger.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .config import CanonicalStage, TIMESTAMP_QUALITY_POLL_OBSERVED


class QuarantineReason(StrEnum):
    BASELINE_NON_UPLOADABLE = "baseline_non_uploadable"
    MISSING_FORM4_EVENT_ID = "missing_form4_event_id"
    AMBIGUOUS_FORM4_IDENTITY = "ambiguous_form4_identity"
    CONFLICTING_FORM_ENTRY_ID = "conflicting_form_entry_id"
    NON_UPLOADABLE_STAGE = "non_uploadable_stage"
    UNMAPPED_STAGE = "unmapped_stage"
    FIRST_POSITIVE_OCCURRENCE_ALREADY_SENT = "first_positive_occurrence_already_sent"
    MULTI_SCHOOL_FANOUT_COLLAPSED = "multi_school_fanout_collapsed"


@dataclass(frozen=True, slots=True)
class Form4Identity:
    """Result of an exact, external Form 4 identity reconciliation.

    ``event_id`` and ``form_entry_id`` are supplied by the CRM side. The two
    ``matched_*`` values come from the authoritative Form 4 record. A caller
    must resolve this before lifecycle evaluation; fuzzy email or phone joins
    are intentionally unsupported.
    """

    event_id: str | None
    form_entry_id: str | None
    matched_event_id: str | None
    matched_form_entry_id: str | None
    match_count: int

    @property
    def is_exact(self) -> bool:
        if not self.event_id or not self.matched_event_id or self.match_count != 1:
            return False
        if self.event_id != self.matched_event_id:
            return False
        return not self.form_entry_id or self.form_entry_id == self.matched_form_entry_id

    @property
    def quarantine_reason(self) -> QuarantineReason | None:
        if not self.event_id:
            return QuarantineReason.MISSING_FORM4_EVENT_ID
        if self.match_count != 1 or self.event_id != self.matched_event_id:
            return QuarantineReason.AMBIGUOUS_FORM4_IDENTITY
        if self.form_entry_id and self.form_entry_id != self.matched_form_entry_id:
            return QuarantineReason.CONFLICTING_FORM_ENTRY_ID
        return None


@dataclass(frozen=True, slots=True)
class CrmOpportunitySnapshot:
    """One current CRM opportunity state, observed by a poller.

    ``opportunity_id_hmac`` must be an HMAC/opaque value, never the native CRM
    opportunity ID. ``school_uuid`` is retained only for reporting; it does not
    participate in activation identity so one parent can fan out to schools.
    """

    opportunity_id_hmac: str
    raw_phase: str | None
    observed_at: datetime
    identity: Form4Identity
    school_uuid: str | None = None
    is_initial_baseline: bool = False


@dataclass(frozen=True, slots=True)
class LifecycleEvent:
    event_id: str
    stage: CanonicalStage
    observed_at: datetime
    opportunity_id_hmac: str
    school_uuid: str | None
    timestamp_quality: str = TIMESTAMP_QUALITY_POLL_OBSERVED

    @property
    def positive_stage_key(self) -> tuple[str, CanonicalStage]:
        return self.event_id, self.stage


@dataclass(frozen=True, slots=True)
class LifecycleDecision:
    snapshot: CrmOpportunitySnapshot
    stage: CanonicalStage | None
    event: LifecycleEvent | None
    quarantine_reason: QuarantineReason | None = None

    @property
    def uploadable(self) -> bool:
        return self.event is not None and self.quarantine_reason is None
