from fastapi import APIRouter, Depends, status

from movienight.api.deps import DbSession, get_current_user
from movienight.schemas.reaction import (
    AddReactionRequest,
    ReactionActionResponse
)
from movienight.services.reaction_service import ReactionService

router = APIRouter(
    prefix="/proposals/{proposal_id}/reactions",
    tags=["reactions"]
)


@router.post(
    "",
    summary="Add food reaction",
    description=(
        "Add a food reaction to a proposal. "
        "Food reactions are available only during the "
        "final hour before the event starts. "
        "If the proposal belongs to a conflict group, "
        "reactions are allowed only for the selected winner. "
        "Hidden reactions are not exposed by the API."
    ),
    response_model=ReactionActionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "content": {
                "application/json": {
                    "example": {
                        "proposal_id": 12,
                        "category": "pizza",
                        "total_for_category": 2,
                        "message": "Reaction added.",
                    }
                }
            }
        },
        400: {
            "content": {
                "application/json": {
                    "examples": {
                        "not_winner": {
                            "summary": "Not the selected winner",
                            "value": {
                                "detail": (
                                    "Food reactions are allowed "
                                    "only for the selected winner "
                                    "during the final hour before start."
                                )
                            },
                        },
                        "duplicate_category": {
                            "summary": "Category already added",
                            "value": {
                                "detail": (
                                    "You have already "
                                    "added this food reaction category."
                                )
                            },
                        },
                    }
                }
            }
        },
        401: {"description": "Authentication required."},
        404: {"description": "Proposal not found."},
    },
)
def add_reaction(
    proposal_id: int,
    payload: AddReactionRequest,
    db: DbSession,
    user=Depends(get_current_user),
) -> ReactionActionResponse:
    return ReactionService(db).add_reaction(
        proposal_id=proposal_id,
        category=payload.category,
        current_user=user,
    )


@router.delete(
    "/{category}",
    summary="Delete food reaction",
    description=(
        "Remove one food reaction category "
        "previously added by the current user. "
        "Food reactions can be removed only "
        "from the currently valid reaction target: "
        "the single proposal itself, or the "
        "winner of a conflict group during the final hour."
    ),
    response_model=ReactionActionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": (
                "Reaction cannot be removed. "
                "Examples: proposal is in the past; "
                "proposal is not the selected winner; "
                "reaction window is not active; user "
                "has not added this category before."
            )
        },
        401: {"description": "Authentication required."},
        404: {"description": "Proposal not found."},
    },
)
def remove_reaction(
    proposal_id: int,
    category: str,
    db: DbSession,
    user=Depends(get_current_user),
) -> ReactionActionResponse:
    return ReactionService(db).remove_reaction(
        proposal_id=proposal_id,
        category=category,
        current_user=user,
    )
