from movienight.core.clock import utcnow
from proxy.services.reaction_proposal_loader import require_proposal
from proxy.services.vote_required import require_vote
from proxy.services.vote_response_builder import build_vote_response
from proxy.services.vote_validation import (
    ensure_vote_removal_allowed,
)


def remove_vote_use_case(
    proposals_repo,
    votes_repo,
    proposal_id: int,
    current_user,
):
    proposal = require_proposal(proposals_repo, proposal_id)
    vote = require_vote(
        votes_repo=votes_repo,
        user_id=current_user.id,
        proposal_id=proposal_id,
    )

    ensure_vote_removal_allowed(
        has_vote=vote is not None,
        proposal=proposal,
        now=utcnow(),
    )

    votes_repo.delete(vote)
    count = votes_repo.count_for_proposal(proposal_id)

    return build_vote_response(
        proposal_id=proposal_id,
        votes_count=count,
        message="Vote removed.",
    )
