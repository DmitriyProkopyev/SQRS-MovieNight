from movienight.services.schedule_exceptions import raise_bad_request
from movienight.services.time_past_check import is_in_past
from movienight.services.time_vote_lock import is_vote_locked


def ensure_vote_not_closed(
    proposal,
    now,
) -> None:
    if is_in_past(proposal.starts_at, now):
        raise_bad_request(
            "Voting is not allowed for this proposal anymore."
        )

    if is_vote_locked(proposal.starts_at, now):
        raise_bad_request(
            "Voting is not allowed for this proposal anymore."
        )
