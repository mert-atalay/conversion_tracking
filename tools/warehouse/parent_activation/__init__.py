"""Pure, stdlib-only rules for parent CRM offline-conversion activation.

This package deliberately contains no network, database, or platform clients.
Callers supply resolved identity and transient match data, then persist only the
safe outputs their storage contract permits.
"""

from .config import CanonicalStage
from .lifecycle import collapse_multi_school_fanout, evaluate_snapshot
from .models import CrmOpportunitySnapshot, Form4Identity, LifecycleDecision

__all__ = [
    "CanonicalStage",
    "CrmOpportunitySnapshot",
    "Form4Identity",
    "LifecycleDecision",
    "collapse_multi_school_fanout",
    "evaluate_snapshot",
]
