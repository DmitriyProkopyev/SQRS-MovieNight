from proxy.services.vote_closed_guard import ensure_vote_not_closed
from proxy.services.vote_duplicate_guard import (
    ensure_not_duplicate_vote,
)
from proxy.services.vote_group_guard import ensure_no_group_vote
from proxy.services.vote_own_proposal_guard import (
    ensure_not_own_proposal,
)


def ensure_vote_allowed(
    proposal,
    current_user_id: int,
    user_votes_in_group: list[int],
    already_voted_for_target: bool,
    now,
) -> None:
    ensure_not_own_proposal(
        proposal=proposal,
        current_user_id=current_user_id,
    )
    ensure_vote_not_closed(
        proposal=proposal,
        now=now,
    )
    ensure_not_duplicate_vote(already_voted_for_target)
    ensure_no_group_vote(user_votes_in_group)
