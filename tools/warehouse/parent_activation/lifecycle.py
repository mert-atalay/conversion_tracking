"""Pure lifecycle eligibility and fanout-collapse rules."""

from __future__ import annotations

from collections.abc import Collection, Iterable
from dataclasses import replace

from .config import NON_UPLOADABLE_STAGE_LABELS, UPLOADABLE_STAGE_LABELS, CanonicalStage
from .models import (
    CrmOpportunitySnapshot,
    LifecycleDecision,
    LifecycleEvent,
    QuarantineReason,
)
from .normalization import normalize_stage_label


def canonical_stage(raw_phase: str | None) -> CanonicalStage | None:
    return UPLOADABLE_STAGE_LABELS.get(normalize_stage_label(raw_phase))


def stage_quarantine_reason(raw_phase: str | None) -> QuarantineReason | None:
    label = normalize_stage_label(raw_phase)
    if label in UPLOADABLE_STAGE_LABELS:
        return None
    if label in NON_UPLOADABLE_STAGE_LABELS:
        return QuarantineReason.NON_UPLOADABLE_STAGE
    return QuarantineReason.UNMAPPED_STAGE


def evaluate_snapshot(
    snapshot: CrmOpportunitySnapshot,
    accepted_positive_stage_keys: Collection[tuple[str, CanonicalStage]] = (),
) -> LifecycleDecision:
    """Evaluate one prospective snapshot without persistence or API calls."""
    if snapshot.is_initial_baseline:
        return LifecycleDecision(snapshot, None, None, QuarantineReason.BASELINE_NON_UPLOADABLE)

    identity_reason = snapshot.identity.quarantine_reason
    if identity_reason:
        return LifecycleDecision(snapshot, None, None, identity_reason)

    stage = canonical_stage(snapshot.raw_phase)
    if stage is None:
        return LifecycleDecision(snapshot, None, None, stage_quarantine_reason(snapshot.raw_phase))

    event_id = snapshot.identity.event_id
    assert event_id is not None  # guarded by Form4Identity.quarantine_reason
    key = (event_id, stage)
    if key in accepted_positive_stage_keys:
        return LifecycleDecision(
            snapshot,
            stage,
            None,
            QuarantineReason.FIRST_POSITIVE_OCCURRENCE_ALREADY_SENT,
        )

    event = LifecycleEvent(
        event_id=event_id,
        stage=stage,
        observed_at=snapshot.observed_at,
        opportunity_id_hmac=snapshot.opportunity_id_hmac,
        school_uuid=snapshot.school_uuid,
    )
    return LifecycleDecision(snapshot, stage, event)


def collapse_multi_school_fanout(decisions: Iterable[LifecycleDecision]) -> list[LifecycleDecision]:
    """Allow one earliest eligible conversion per Form 4 event and stage.

    A parent inquiry can yield several school opportunities. Each remains in the
    lifecycle audit stream, but only one becomes an activation candidate.
    """
    materialized = list(decisions)
    winners: dict[tuple[str, CanonicalStage], LifecycleDecision] = {}
    for decision in materialized:
        if not decision.uploadable or decision.event is None:
            continue
        key = decision.event.positive_stage_key
        previous = winners.get(key)
        if previous is None or _fanout_sort_key(decision) < _fanout_sort_key(previous):
            winners[key] = decision

    collapsed: list[LifecycleDecision] = []
    for decision in materialized:
        if not decision.uploadable or decision.event is None:
            collapsed.append(decision)
            continue
        if winners[decision.event.positive_stage_key] is decision:
            collapsed.append(decision)
            continue
        collapsed.append(
            replace(
                decision,
                event=None,
                quarantine_reason=QuarantineReason.MULTI_SCHOOL_FANOUT_COLLAPSED,
            )
        )
    return collapsed


def _fanout_sort_key(decision: LifecycleDecision) -> tuple[object, str]:
    assert decision.event is not None
    return decision.event.observed_at, decision.event.opportunity_id_hmac
