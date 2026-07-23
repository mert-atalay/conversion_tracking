#!/usr/bin/env python3
"""Read-only GreenRope parent lifecycle poller.

``baseline`` records the current opportunity states as permanently
non-uploadable.  ``poll`` records only new/changed states as prospective
``poll_observed`` candidates.  This command never calls Google, Meta,
KinderTales, or any GreenRope write endpoint.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from parent_activation.greenrope_adapter import (
    DEFAULT_ENDPOINT,
    GreenRopeClient,
    as_unresolved_form4_identity,
    compare_to_previous,
    evaluate_required_fields,
    fetch_group_opportunities,
    parse_opportunity,
)
from parent_activation.lifecycle import canonical_stage, evaluate_snapshot, stage_quarantine_reason
from parent_activation.models import CrmOpportunitySnapshot


STATE_VERSION = 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only prospective GreenRope parent lifecycle poller")
    parser.add_argument("--mode", required=True, choices=("dictionary-only", "baseline", "poll"))
    parser.add_argument("--state-file", help="Restricted local state file; required for baseline and poll modes.")
    parser.add_argument("--group-ids", help="Optional comma-separated GreenRope group IDs for controlled reads.")
    parser.add_argument("--max-workers", type=int, default=int(os.environ.get("GREENROPE_MAX_CONCURRENT_GROUP_CALLS", "4")))
    parser.add_argument("--request-timeout", type=int, default=int(os.environ.get("GREENROPE_REQUEST_TIMEOUT_SECONDS", "120")))
    return parser.parse_args()


def _credentials() -> tuple[str, str, str, str]:
    email = os.environ.get("GREENROPE_EMAIL") or os.environ.get("GR_EMAIL")
    token = os.environ.get("GREENROPE_TOKEN") or os.environ.get("GR_TOKEN") or os.environ.get("GREENROPE_AUTH_TOKEN")
    account_id = os.environ.get("GREENROPE_ACCOUNT_ID") or os.environ.get("GR_ACCOUNT")
    endpoint = os.environ.get("GREENROPE_API_URL") or os.environ.get("GR_ENDPOINT") or DEFAULT_ENDPOINT
    if not all((email, token, account_id)):
        raise SystemExit("Missing GREENROPE_EMAIL, GREENROPE_TOKEN, or GREENROPE_ACCOUNT_ID")
    return endpoint, email, token, account_id


def _load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": STATE_VERSION, "baseline_established": False, "opportunities": {}}
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("version") != STATE_VERSION or not isinstance(state.get("opportunities"), dict):
        raise RuntimeError("Invalid lifecycle state file")
    return state


def _write_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(state, handle, sort_keys=True, separators=(",", ":"))
        handle.write("\n")
        temporary = Path(handle.name)
    os.chmod(temporary, 0o600)
    temporary.replace(path)


def _safe_dictionary_output(client: GreenRopeClient) -> dict[str, object]:
    fields = client.opportunity_fields()
    readiness = evaluate_required_fields(field.normalized_label for field in fields)
    return {
        "mode": "dictionary-only",
        "readiness": readiness.to_safe_dict(),
        "field_count": len(fields),
        "fields": [asdict(field) for field in fields],
        "phases": [asdict(phase) for phase in client.phases()],
        "phase_paths": [asdict(path) for path in client.phase_paths()],
    }


def main() -> None:
    args = parse_args()
    if not 1 <= args.max_workers <= 4:
        raise SystemExit("--max-workers must be between 1 and 4")
    endpoint, email, token, account_id = _credentials()
    client = GreenRopeClient(endpoint, email, token, account_id, args.request_timeout)

    if args.mode == "dictionary-only":
        print(json.dumps(_safe_dictionary_output(client), sort_keys=True))
        return
    if not args.state_file:
        raise SystemExit("--state-file is required for baseline and poll modes")
    secret = os.environ.get("PARENT_ACTIVATION_HMAC_SECRET")
    if not secret:
        raise SystemExit("PARENT_ACTIVATION_HMAC_SECRET is required for baseline and poll modes")

    fields = client.opportunity_fields()
    readiness = evaluate_required_fields(field.normalized_label for field in fields)
    groups = client.groups()
    if args.group_ids:
        allowed = {item.strip() for item in args.group_ids.split(",") if item.strip()}
        groups = [group for group in groups if group["id"] in allowed]
    fetched, group_errors = fetch_group_opportunities(client, groups, max_workers=args.max_workers)
    observed_at = datetime.now(timezone.utc)
    parsed = [
        parse_opportunity(row, group_id=group_id, hmac_secret=secret)
        for group_id, rows in fetched
        for row in rows
    ]

    state_file = Path(args.state_file)
    state = _load_state(state_file)
    if args.mode == "baseline" and state["baseline_established"]:
        raise SystemExit("Baseline already exists; use poll mode so baseline states can never be reclassified")
    if args.mode == "poll" and not state["baseline_established"]:
        raise SystemExit("A baseline is required before poll mode")

    is_baseline = args.mode == "baseline"
    observations = compare_to_previous(parsed, state["opportunities"], observed_at=observed_at, baseline=is_baseline)
    candidates: list[dict[str, str | None]] = []
    if readiness.status == "ready":
        for observation in observations:
            if observation.is_initial_baseline or not observation.phase_changed:
                continue
            phase_reason = stage_quarantine_reason(observation.opportunity.raw_phase)
            if phase_reason is not None:
                candidates.append(
                    {
                        "opportunity_id_hmac": observation.opportunity.opportunity_id_hmac,
                        "canonical_stage": None,
                        "quarantine_reason": phase_reason.value,
                        "timestamp_quality": "poll_observed",
                    }
                )
                continue
            snapshot = CrmOpportunitySnapshot(
                opportunity_id_hmac=observation.opportunity.opportunity_id_hmac,
                raw_phase=observation.opportunity.raw_phase,
                observed_at=observation.observed_at,
                identity=as_unresolved_form4_identity(observation.opportunity),
                school_uuid=observation.opportunity.school_uuid,
            )
            decision = evaluate_snapshot(snapshot)
            candidates.append(
                {
                    "opportunity_id_hmac": observation.opportunity.opportunity_id_hmac,
                    "canonical_stage": str(canonical_stage(observation.opportunity.raw_phase) or "") or None,
                    "quarantine_reason": decision.quarantine_reason.value if decision.quarantine_reason else None,
                    "timestamp_quality": "poll_observed",
                }
            )

    for opportunity in parsed:
        record = opportunity.state_record()
        record["observed_at"] = observed_at.isoformat().replace("+00:00", "Z")
        record["initial_baseline_non_uploadable"] = bool(
            is_baseline or state["opportunities"].get(opportunity.opportunity_id_hmac, {}).get("initial_baseline_non_uploadable")
        )
        state["opportunities"][opportunity.opportunity_id_hmac] = record
    state["baseline_established"] = True
    state["baseline_at"] = state.get("baseline_at") or observed_at.isoformat().replace("+00:00", "Z")
    _write_state(state_file, state)

    print(
        json.dumps(
            {
                "mode": args.mode,
                "readiness": readiness.to_safe_dict(),
                "observed_at": observed_at.isoformat().replace("+00:00", "Z"),
                "groups_requested": len(groups),
                "group_error_count": len(group_errors),
                "opportunities_observed": len(parsed),
                "baseline_non_uploadable_count": sum(item.is_initial_baseline for item in observations),
                "phase_change_count": sum(item.phase_changed for item in observations),
                "lifecycle_candidates": candidates,
                "lifecycle_candidate_count": len(candidates),
                "activation_status": "blocked_field_contract" if readiness.status != "ready" else "identity_reconciliation_required",
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
