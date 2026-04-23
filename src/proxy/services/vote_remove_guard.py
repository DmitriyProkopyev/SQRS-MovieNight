from datetime import datetime

from proxy.db.models import Proposal
from proxy.services.schedule_exceptions import raise_bad_request
from proxy.services.time_past_check import is_in_past
from proxy.services.time_vote_lock import is_vote_locked


def ensure_vote_removal_allowed(
    has_vote: bool,
    proposal: Proposal,
    now: datetime,
) -> None:
    if not has_vote:
        raise_bad_request("You have not voted for this proposal.")

    if is_in_past(proposal.starts_at, now):
        raise_bad_request(
            "Vote cancellation is not allowed for this proposal anymore."
        )

    if is_vote_locked(proposal.starts_at, now):
        raise_bad_request(
            "Vote cancellation is not allowed for this proposal anymore."
        )
