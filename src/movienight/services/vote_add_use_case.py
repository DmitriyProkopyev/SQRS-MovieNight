from movienight.core.clock import utcnow
from movienight.db.models import Vote
from movienight.services.vote_group_context import build_vote_group_context
from movienight.services.vote_response_builder import build_vote_response
from movienight.services.vote_validation import ensure_vote_allowed


def add_vote_use_case(
    proposals_repo,
    votes_repo,
    proposal_id: int,
    current_user,
):
    context = build_vote_group_context(
        proposals_repo=proposals_repo,
        votes_repo=votes_repo,
        proposal_id=proposal_id,
        current_user_id=current_user.id,
    )

    ensure_vote_allowed(
        proposal=context["proposal"],
        current_user_id=current_user.id,
        user_votes_in_group=[
            vote.proposal_id for vote in context["user_votes"]
        ],
        already_voted_for_target=context["already_voted_for_target"],
        now=utcnow(),
    )

    votes_repo.create(
        Vote(
            user_id=current_user.id,
            proposal_id=proposal_id,
            created_at=utcnow(),
        )
    )
    count = votes_repo.count_for_proposal(proposal_id)

    return build_vote_response(
        proposal_id=proposal_id,
        votes_count=count,
        message="Vote added.",
    )
