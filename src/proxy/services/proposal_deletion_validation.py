from datetime import datetime

from proxy.db.models import Proposal
from proxy.services.schedule_exceptions import (
    raise_bad_request,
    raise_forbidden,
)
from proxy.services.schedule_time_rules import is_in_past


def ensure_deletion_allowed(
    proposal: Proposal,
    current_user_id: int,
    now: datetime,
) -> None:
    if proposal.creator_id != current_user_id:
        raise_forbidden("You can delete only your own proposals.")

    if is_in_past(proposal.starts_at, now):
        raise_bad_request("Past proposals cannot be deleted.")
