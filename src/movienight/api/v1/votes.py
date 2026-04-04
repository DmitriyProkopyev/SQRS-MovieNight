from fastapi import APIRouter, Depends, status

from movienight.api.deps import DbSession, get_current_user
from movienight.schemas.vote import VoteActionResponse
from movienight.services.vote_service import VoteService

router = APIRouter(prefix="/proposals/{proposal_id}/votes", tags=["votes"])


@router.post(
    "",
    summary="Vote for proposal",
    description=(
        "Add the current user's vote to a proposal. "
        "A user cannot vote for their own proposal, cannot vote twice for the same proposal, "
        "and cannot vote for two different proposals inside the same conflict group. "
        "Voting is closed for past proposals and for proposals starting in 1 hour or less."
    ),
    response_model=VoteActionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "description": (
                "Voting is not allowed. "
                "Examples: user tries to vote for own proposal; proposal is in the past; "
                "proposal starts in 1 hour or less; user already voted for this proposal; "
                "user already voted for another proposal in the same conflict group."
            )
        },
        401: {"description": "Authentication required."},
        404: {"description": "Proposal not found."},
    },
)
def add_vote(
    proposal_id: int,
    db: DbSession,
    user=Depends(get_current_user),
) -> VoteActionResponse:
    return VoteService(db).add_vote(proposal_id=proposal_id, current_user=user)


@router.delete(
    "",
    summary="Cancel vote",
    description=(
        "Remove the current user's vote from a proposal. "
        "Vote cancellation is allowed only if the user has already voted and the proposal is not in the past "
        "and does not start in 1 hour or less."
    ),
    response_model=VoteActionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": (
                "Vote cancellation is not allowed. "
                "Examples: user has not voted for this proposal; proposal is in the past; "
                "proposal starts in 1 hour or less."
            )
        },
        401: {"description": "Authentication required."},
        404: {"description": "Proposal not found."},
    },
)
def remove_vote(
    proposal_id: int,
    db: DbSession,
    user=Depends(get_current_user),
) -> VoteActionResponse:
    return VoteService(db).remove_vote(proposal_id=proposal_id, current_user=user)