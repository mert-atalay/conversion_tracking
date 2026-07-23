"""Narrow GreenRope writer for the two governed Form 4 identity fields."""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import escape

from .greenrope_adapter import GreenRopeClient
from .identity_bridge import (
    GreenRopeIdentityCandidate,
    parse_greenrope_candidate,
)


_CLOSE_DATE_RE = re.compile(r"^\d{8}$")


@dataclass(frozen=True, slots=True)
class IdentityWriteResult:
    request_succeeded: bool
    readback_confirmed: bool


def build_identity_edit_xml(
    *,
    account_id: str,
    candidate: GreenRopeIdentityCandidate,
    event_id: str,
    form_entry_id: str,
) -> str:
    if not candidate.quality:
        raise ValueError("GreenRope Quality is required for identity edit")
    if not _CLOSE_DATE_RE.fullmatch(candidate.close_date):
        raise ValueError("GreenRope CloseDate is required for identity edit")
    values = {
        "account_id": account_id,
        "opportunity_id": candidate.raw_opportunity_id,
        "quality": candidate.quality,
        "close_date": candidate.close_date,
        "event_id": event_id,
        "form_entry_id": form_entry_id,
    }
    safe = {key: escape(value, quote=True) for key, value in values.items()}
    return (
        "<EditOpportunitiesRequest>"
        "<Opportunities>"
        f'<Opportunity account_id="{safe["account_id"]}" '
        f'opportunity_id="{safe["opportunity_id"]}">'
        f'<Quality>{safe["quality"]}</Quality>'
        f'<CloseDate>{safe["close_date"]}</CloseDate>'
        "<CustomFields>"
        f'<CustomField fieldname="cefa_event_id">{safe["event_id"]}</CustomField>'
        f'<CustomField fieldname="cefa_form_entry_id">{safe["form_entry_id"]}</CustomField>'
        "</CustomFields>"
        "</Opportunity>"
        "</Opportunities>"
        "</EditOpportunitiesRequest>"
    )


def response_succeeded(payload: object) -> bool:
    text = str(payload).lower()
    return "success" in text and "error" not in text and "invalid" not in text


class GreenRopeIdentityWriter:
    """Write exact identity only, then prove it with a group read-back."""

    def __init__(self, client: GreenRopeClient, *, hmac_secret: bytes) -> None:
        self.client = client
        self.hmac_secret = hmac_secret

    def write_and_confirm(
        self,
        *,
        candidate: GreenRopeIdentityCandidate,
        event_id: str,
        form_entry_id: str,
    ) -> IdentityWriteResult:
        payload = self.client.call(
            build_identity_edit_xml(
                account_id=self.client.account_id,
                candidate=candidate,
                event_id=event_id,
                form_entry_id=form_entry_id,
            )
        )
        if not response_succeeded(payload):
            return IdentityWriteResult(False, False)
        for raw in self.client.opportunities(candidate.group_id):
            parsed = parse_greenrope_candidate(
                raw,
                group_id=candidate.group_id,
                secret=self.hmac_secret,
            )
            if parsed.opportunity_id_hmac != candidate.opportunity_id_hmac:
                continue
            return IdentityWriteResult(
                True,
                parsed.current_event_id == event_id
                and parsed.current_form_entry_id == form_entry_id,
            )
        return IdentityWriteResult(True, False)
