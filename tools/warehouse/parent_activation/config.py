"""Stable activation policy constants.

Changing a stage map changes conversion meaning. Keep additions explicit and
covered by tests rather than silently treating a new CRM phase as uploadable.
"""

from __future__ import annotations

from datetime import timedelta
from enum import StrEnum
from types import MappingProxyType


class CanonicalStage(StrEnum):
    TOUR_SCHEDULED = "tour_scheduled"
    TOUR_COMPLETED_CANDIDATE = "tour_completed_candidate"
    CRM_CLOSED_WON = "crm_closed_won"


TIMESTAMP_QUALITY_POLL_OBSERVED = "poll_observed"
GOOGLE_CLICK_ID_MAX_AGE = timedelta(days=90)
GOOGLE_USER_DATA_MAX_AGE = timedelta(days=63)
META_EVENT_MAX_AGE = timedelta(days=7)

# Keys are normalized by normalization.normalize_stage_label().
UPLOADABLE_STAGE_LABELS = MappingProxyType(
    {
        "tour scheduled": CanonicalStage.TOUR_SCHEDULED,
        "tour_scheduled": CanonicalStage.TOUR_SCHEDULED,
        "post tour": CanonicalStage.TOUR_COMPLETED_CANDIDATE,
        "post_tour": CanonicalStage.TOUR_COMPLETED_CANDIDATE,
        "enrollment closed won": CanonicalStage.CRM_CLOSED_WON,
        "enrollment_closed_won": CanonicalStage.CRM_CLOSED_WON,
        "closed won": CanonicalStage.CRM_CLOSED_WON,
        "closed_won": CanonicalStage.CRM_CLOSED_WON,
    }
)

# These values are known non-conversion outcomes. Unknown labels are handled
# separately so a new GreenRope phase surfaces as a QA issue.
NON_UPLOADABLE_STAGE_LABELS = frozenset(
    {
        "nurturing",
        "lost",
        "closed lost",
        "closed_lost",
        "tour missed",
        "tour_missed",
        "missed",
    }
)
