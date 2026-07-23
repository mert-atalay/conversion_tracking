"""BQ-backed GreenRope lifecycle poll and outbox construction."""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Mapping

from .bigquery_store import (
    BASELINE_NON_UPLOADABLE,
    NOT_QUARANTINED,
    QUARANTINED,
    OutboxIdentity,
    ParentActivationBigQueryStore,
    hmac_hex,
)
from .config import CanonicalStage, ConsentState
from .greenrope_adapter import (
    ParsedOpportunity,
    PollObservation,
    compare_to_previous,
    evaluate_required_fields,
    fetch_group_opportunities,
    parse_opportunity,
)
from .lifecycle import (
    canonical_stage,
    collapse_multi_school_fanout,
    evaluate_snapshot,
    stage_quarantine_reason,
)
from .meta_capi import CRM_STAGE_EVENT_NAMES, META_DATASET_ID
from .models import (
    CrmOpportunitySnapshot,
    Form4Identity,
    LifecycleDecision,
    QuarantineReason,
)
from .normalization import normalize_stage_label
from .repository import Form4Match, ParentActivationRepository


GOOGLE_ADS_ACCOUNT_ID = "4159217891"
STAGE_MAPPING_VERSION = "parent_greenrope_stage_v1"
SOURCE_ACCOUNT = "cefa_parent_form4_greenrope"
MATCH_KEY_RETENTION_DAYS = 100
ALLOWED_ACTIVATION_MODES = frozenset(
    {"disabled", "dry_run", "validate_only", "test", "secondary_production"}
)


@dataclass(frozen=True, slots=True)
class PollRunResult:
    mode: str
    field_contract_ready: bool
    baseline_established: bool
    opportunities_observed: int
    phase_changes: int
    lifecycle_events: int
    outbox_rows: int
    quarantined_events: int
    group_errors: int

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "field_contract_ready": self.field_contract_ready,
            "baseline_established": self.baseline_established,
            "opportunities_observed": self.opportunities_observed,
            "phase_changes": self.phase_changes,
            "lifecycle_events": self.lifecycle_events,
            "outbox_rows": self.outbox_rows,
            "quarantined_events": self.quarantined_events,
            "group_errors": self.group_errors,
        }


def _utc_timestamp(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _activation_mode(value: str | None) -> str:
    mode = str(value or "disabled").strip().lower()
    if mode not in ALLOWED_ACTIVATION_MODES:
        raise ValueError(f"unsupported PARENT_ACTIVATION_MODE: {mode}")
    return mode


def _consent_state(value: str | None) -> ConsentState:
    try:
        return ConsentState(str(value or ConsentState.UNKNOWN).strip().lower())
    except ValueError as exc:
        raise ValueError("unsupported PARENT_ACTIVATION_CONSENT_STATE") from exc


def _google_destinations(value: str | None) -> dict[str, str]:
    if not value:
        return {}
    parsed = json.loads(value)
    if not isinstance(parsed, Mapping):
        raise ValueError("PARENT_GOOGLE_DESTINATIONS_JSON must be an object")
    destinations: dict[str, str] = {}
    for stage, action_id in parsed.items():
        canonical = str(stage).strip()
        numeric = str(action_id).strip()
        if canonical not in {item.value for item in CanonicalStage}:
            raise ValueError(f"unsupported Google destination stage: {canonical}")
        if not numeric.isdigit():
            raise ValueError("Google destination IDs must be bare numeric IDs")
        destinations[canonical] = numeric
    return destinations


def select_controlled_groups(
    groups: Iterable[Mapping[str, Any]],
    group_ids: set[str] | None,
) -> list[dict[str, str]]:
    if not group_ids:
        raise ValueError("parent GreenRope group allowlist is required")
    normalized = [
        {"id": str(group["id"]), "name": str(group.get("name") or "")}
        for group in groups
    ]
    available = {group["id"] for group in normalized}
    missing = sorted(group_ids - available)
    if missing:
        raise ValueError(
            "parent GreenRope group allowlist contains unknown IDs: "
            + ", ".join(missing)
        )
    return [group for group in normalized if group["id"] in group_ids]


def _attribution_platform(opportunity: ParsedOpportunity) -> str | None:
    values = opportunity.match_values
    if any((values.gclid, values.gbraid, values.wbraid)):
        return "google"
    if any((values.fbclid, values.fbc, values.fbp)):
        return "meta"
    source = str(opportunity.utm_source or "").lower()
    medium = str(opportunity.utm_medium or "").lower()
    if source == "google" or medium in {"cpc", "ppc", "paid_search"}:
        return "google"
    if source in {"meta", "facebook", "instagram"} or medium in {
        "paid_social",
        "paidsocial",
    }:
        return "meta"
    return None


def build_snapshot_rows(
    opportunities: Iterable[ParsedOpportunity],
    *,
    observed_at: datetime,
    poll_run_id: str,
    baseline: bool,
    previous_state: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for opportunity in opportunities:
        is_first_seen = opportunity.opportunity_id_hmac not in previous_state
        is_initial = baseline or is_first_seen
        stage = canonical_stage(opportunity.raw_phase)
        values = opportunity.match_values
        rows.append(
            {
                "snapshot_at": _utc_timestamp(observed_at),
                "snapshot_date": observed_at.date().isoformat(),
                "poll_run_id": poll_run_id,
                "opportunity_id_hmac": opportunity.opportunity_id_hmac,
                "governed_lead_id_hmac": None,
                "form4_event_id": opportunity.form4_event_id,
                "form_entry_id": opportunity.form_entry_id,
                "greenrope_group_id": opportunity.group_id,
                "school_uuid": opportunity.school_uuid,
                "opportunity_created_at": None,
                "source_modified_at": None,
                "source_modified_at_quality": "poll_observed",
                "raw_phase": opportunity.raw_phase,
                "canonical_stage": stage.value if stage else None,
                "stage_mapping_version": STAGE_MAPPING_VERSION,
                "is_initial_baseline": is_initial,
                "baseline_status": (
                    BASELINE_NON_UPLOADABLE if is_initial else "prospective_observation"
                ),
                "attribution_platform": _attribution_platform(opportunity),
                "has_gclid": bool(values.gclid),
                "has_gbraid": bool(values.gbraid),
                "has_wbraid": bool(values.wbraid),
                "has_fbc": bool(values.fbc),
                "has_fbp": bool(values.fbp),
                "has_email_hash": bool(values.email_sha256),
                "has_phone_hash": bool(values.phone_sha256),
                "pii_redacted": True,
                "loaded_at": _utc_timestamp(observed_at),
            }
        )
    return rows


def _identity_for(
    opportunity: ParsedOpportunity,
    matches: Mapping[str, Form4Match],
) -> Form4Identity:
    if not opportunity.form4_event_id:
        return Form4Identity(None, opportunity.form_entry_id, None, None, 0)
    match = matches.get(opportunity.form4_event_id)
    if match is None:
        return Form4Identity(
            opportunity.form4_event_id,
            opportunity.form_entry_id,
            None,
            None,
            0,
        )
    return Form4Identity(
        opportunity.form4_event_id,
        opportunity.form_entry_id,
        match.identity.matched_event_id,
        match.identity.matched_form_entry_id,
        match.identity.match_count,
    )


def build_lifecycle_decisions(
    observations: Iterable[PollObservation],
    matches: Mapping[str, Form4Match],
) -> list[LifecycleDecision]:
    decisions: list[LifecycleDecision] = []
    for observation in observations:
        if observation.is_initial_baseline or not observation.phase_changed:
            continue
        match = (
            matches.get(observation.opportunity.form4_event_id or "")
            if observation.opportunity.form4_event_id
            else None
        )
        snapshot = CrmOpportunitySnapshot(
            opportunity_id_hmac=observation.opportunity.opportunity_id_hmac,
            raw_phase=observation.opportunity.raw_phase,
            observed_at=observation.observed_at,
            identity=_identity_for(observation.opportunity, matches),
            school_uuid=match.school_uuid if match else observation.opportunity.school_uuid,
        )
        decision = evaluate_snapshot(snapshot)
        if match and match.is_test:
            decision = LifecycleDecision(
                snapshot=decision.snapshot,
                stage=decision.stage,
                event=None,
                quarantine_reason=QuarantineReason.TEST_RECORD,
            )
        decisions.append(decision)
    return collapse_multi_school_fanout(decisions)


def build_lifecycle_rows(
    observations: Iterable[PollObservation],
    decisions: Iterable[LifecycleDecision],
    *,
    secret: bytes,
    observed_at: datetime,
) -> list[dict[str, Any]]:
    decision_by_opportunity = {
        decision.snapshot.opportunity_id_hmac: decision for decision in decisions
    }
    rows: list[dict[str, Any]] = []
    for observation in observations:
        if observation.is_initial_baseline or not observation.phase_changed:
            continue
        opportunity = observation.opportunity
        decision = decision_by_opportunity[opportunity.opportunity_id_hmac]
        stage = decision.stage
        reason = (
            decision.quarantine_reason.value
            if decision.quarantine_reason is not None
            else None
        )
        if stage is None and reason is None:
            phase_reason = stage_quarantine_reason(opportunity.raw_phase)
            reason = phase_reason.value if phase_reason else "non_uploadable_stage"
        canonical_value = (
            stage.value
            if stage
            else (
                "non_uploadable"
                if normalize_stage_label(opportunity.raw_phase)
                else "unmapped"
            )
        )
        event_id = hmac_hex(
            secret,
            "cefa_parent_lifecycle_v1",
            opportunity.opportunity_id_hmac,
            normalize_stage_label(opportunity.raw_phase) or "unmapped",
            _utc_timestamp(observation.observed_at),
        )
        rows.append(
            {
                "lifecycle_event_id": event_id,
                "opportunity_id_hmac": opportunity.opportunity_id_hmac,
                "stage_sequence": 1,
                "previous_stage": None,
                "canonical_stage": canonical_value,
                "raw_phase": opportunity.raw_phase,
                "stage_occurred_at": _utc_timestamp(observation.observed_at),
                "first_observed_at": _utc_timestamp(observation.observed_at),
                "previous_observed_at": None,
                "timestamp_quality": "poll_observed",
                "timestamp_uncertainty_seconds": None,
                "event_source": "greenrope_api_poll",
                "is_initial_baseline": False,
                "form4_event_id": opportunity.form4_event_id,
                "form_entry_id": opportunity.form_entry_id,
                "school_uuid": decision.snapshot.school_uuid,
                "attribution_platform": _attribution_platform(opportunity),
                "eligibility_status": "eligible" if decision.uploadable else "quarantined",
                "eligibility_reasons": [] if decision.uploadable else [reason],
                "quarantine_status": NOT_QUARANTINED if decision.uploadable else QUARANTINED,
                "quarantine_reason": None if decision.uploadable else reason,
                "created_at": _utc_timestamp(observed_at),
            }
        )
    return rows


def _match_key_reason(
    platform: str,
    opportunity: ParsedOpportunity,
    match: Form4Match,
    consent: ConsentState,
) -> str | None:
    if match.is_test:
        return "test_record"
    if not match.identity.is_exact:
        reason = match.identity.quarantine_reason
        return reason.value if reason else "ambiguous_form4_identity"
    if consent is not ConsentState.GRANTED:
        return f"consent_{consent.value}"
    values = opportunity.match_values
    if platform == "google":
        if not any(
            (
                match.gclid,
                match.gbraid,
                match.wbraid,
                values.email_sha256,
                values.phone_sha256,
            )
        ):
            return "missing_google_match_key"
    elif not any(
        (values.email_sha256, values.phone_sha256, values.fbc, values.fbp)
    ):
        return "missing_meta_match_key"
    return None


def _upsert_match_key(
    repository: ParentActivationRepository,
    *,
    opportunity: ParsedOpportunity,
    match: Form4Match,
    secret: bytes,
    consent: ConsentState,
    observed_at: datetime,
) -> str:
    assert opportunity.form4_event_id is not None
    captured_at = match.submitted_at or observed_at
    match_key_ref = hmac_hex(
        secret,
        "cefa_parent_match_key_v1",
        opportunity.form4_event_id,
    )
    values = opportunity.match_values
    repository.upsert_match_key(
        {
            "captured_date": captured_at.date().isoformat(),
            "form4_event_id": opportunity.form4_event_id,
            "opportunity_id_hmac": opportunity.opportunity_id_hmac,
            "governed_lead_id_hmac": hmac_hex(
                secret,
                "cefa_parent_lead_v1",
                opportunity.form4_event_id,
            ),
            "email_sha256": values.email_sha256,
            "phone_sha256": values.phone_sha256,
            "gclid": match.gclid or values.gclid,
            "gbraid": match.gbraid or values.gbraid,
            "wbraid": match.wbraid or values.wbraid,
            "fbc": values.fbc,
            "fbp": values.fbp,
            "click_id_captured_at": _utc_timestamp(captured_at),
            "user_data_captured_at": _utc_timestamp(captured_at),
            "match_key_source": "form4_exact_identity_greenrope_transient_hash",
            "consent_status": consent.value,
            "expires_at": _utc_timestamp(
                captured_at + timedelta(days=MATCH_KEY_RETENTION_DAYS)
            ),
            "loaded_at": _utc_timestamp(observed_at),
        }
    )
    return match_key_ref


def build_and_enqueue_outbox(
    decisions: Iterable[LifecycleDecision],
    opportunities: Mapping[str, ParsedOpportunity],
    matches: Mapping[str, Form4Match],
    *,
    repository: ParentActivationRepository,
    store: ParentActivationBigQueryStore,
    secret: bytes,
    activation_mode: str,
    consent: ConsentState,
    google_destinations: Mapping[str, str],
    observed_at: datetime,
) -> int:
    if activation_mode == "disabled":
        return 0
    count = 0
    for decision in decisions:
        if not decision.uploadable or decision.event is None:
            continue
        event = decision.event
        opportunity = opportunities[event.opportunity_id_hmac]
        match = matches.get(event.event_id)
        if match is None:
            continue
        match_ref = _upsert_match_key(
            repository,
            opportunity=opportunity,
            match=match,
            secret=secret,
            consent=consent,
            observed_at=observed_at,
        )
        subject_id = hmac_hex(secret, "cefa_parent_subject_v1", event.event_id)
        lifecycle_event_id = hmac_hex(
            secret,
            "cefa_parent_lifecycle_v1",
            event.opportunity_id_hmac,
            normalize_stage_label(opportunity.raw_phase) or "unmapped",
            _utc_timestamp(event.observed_at),
        )
        for platform in ("google", "meta"):
            stage_value = event.stage.value
            destination_action_key = (
                google_destinations.get(stage_value)
                if platform == "google"
                else CRM_STAGE_EVENT_NAMES[stage_value]
            )
            reason = _match_key_reason(platform, opportunity, match, consent)
            if not match.school_uuid:
                reason = reason or "missing_form4_school_uuid"
            if destination_action_key is None:
                reason = reason or "destination_not_configured"
                destination_action_key = f"pending_{stage_value}"
            outbox = store.build_outbox_row(
                selected_lifecycle_event_id=lifecycle_event_id,
                identity=OutboxIdentity(
                    form4_event_id=event.event_id,
                    canonical_stage=stage_value,
                    platform=platform,
                    destination_action_key=destination_action_key,
                ),
                activation_subject_id_hmac=subject_id,
                activation_identity_scope="form4_event",
                source_lifecycle_event_count=1,
                source_is_initial_baseline=False,
                school_uuid=match.school_uuid or "unknown_school",
                destination_account_id=(
                    GOOGLE_ADS_ACCOUNT_ID if platform == "google" else META_DATASET_ID
                ),
                platform_event_name=(
                    destination_action_key
                    if platform == "google"
                    else CRM_STAGE_EVENT_NAMES[stage_value]
                ),
                event_timestamp=event.observed_at,
                match_key_ref=match_ref,
                activation_mode=activation_mode,
                quarantine_reason=reason,
            )
            store.enqueue_outbox(outbox)
            count += 1
    return count


def run_poll(
    *,
    client: Any,
    repository: ParentActivationRepository,
    store: ParentActivationBigQueryStore,
    secret: bytes,
    activation_mode: str | None = None,
    consent_state: str | None = None,
    google_destinations_json: str | None = None,
    group_ids: set[str] | None = None,
    max_workers: int = 4,
    observed_at: datetime | None = None,
) -> PollRunResult:
    now = (observed_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    mode = _activation_mode(
        activation_mode
        if activation_mode is not None
        else os.environ.get("PARENT_ACTIVATION_MODE")
    )
    consent = _consent_state(
        consent_state
        if consent_state is not None
        else os.environ.get("PARENT_ACTIVATION_CONSENT_STATE")
    )
    destinations = _google_destinations(
        google_destinations_json
        if google_destinations_json is not None
        else os.environ.get("PARENT_GOOGLE_DESTINATIONS_JSON")
    )
    fields = client.opportunity_fields()
    readiness = evaluate_required_fields(item.normalized_label for item in fields)
    groups = select_controlled_groups(client.groups(), group_ids)
    fetched, group_errors = fetch_group_opportunities(
        client,
        groups,
        max_workers=max_workers,
    )
    parsed = [
        parse_opportunity(row, group_id=group_id, hmac_secret=secret)
        for group_id, rows in fetched
        for row in rows
    ]
    previous = repository.latest_states()
    baseline = not repository.baseline_exists()
    observations = compare_to_previous(
        parsed,
        previous,
        observed_at=now,
        baseline=baseline,
    )
    poll_run_id = str(uuid.uuid4())
    repository.insert_state_snapshots(
        build_snapshot_rows(
            parsed,
            observed_at=now,
            poll_run_id=poll_run_id,
            baseline=baseline,
            previous_state=previous,
        )
    )
    changed = [
        item
        for item in observations
        if not item.is_initial_baseline and item.phase_changed
    ]
    event_ids = {
        item.opportunity.form4_event_id
        for item in changed
        if item.opportunity.form4_event_id
    }
    entry_ids = {
        item.opportunity.form4_event_id: item.opportunity.form_entry_id
        for item in changed
        if item.opportunity.form4_event_id
    }
    matches = (
        repository.resolve_form4_matches(event_ids, entry_ids)
        if readiness.status == "ready"
        else {}
    )
    decisions = (
        build_lifecycle_decisions(changed, matches)
        if readiness.status == "ready"
        else []
    )
    lifecycle_rows = (
        build_lifecycle_rows(changed, decisions, secret=secret, observed_at=now)
        if readiness.status == "ready"
        else []
    )
    repository.insert_lifecycle_events(lifecycle_rows)
    by_opportunity = {
        opportunity.opportunity_id_hmac: opportunity for opportunity in parsed
    }
    outbox_count = (
        build_and_enqueue_outbox(
            decisions,
            by_opportunity,
            matches,
            repository=repository,
            store=store,
            secret=secret,
            activation_mode=mode,
            consent=consent,
            google_destinations=destinations,
            observed_at=now,
        )
        if readiness.status == "ready"
        else 0
    )
    return PollRunResult(
        mode=mode,
        field_contract_ready=readiness.status == "ready",
        baseline_established=baseline,
        opportunities_observed=len(parsed),
        phase_changes=len(changed),
        lifecycle_events=len(lifecycle_rows),
        outbox_rows=outbox_count,
        quarantined_events=sum(
            row["quarantine_status"] == QUARANTINED for row in lifecycle_rows
        ),
        group_errors=len(group_errors),
    )
