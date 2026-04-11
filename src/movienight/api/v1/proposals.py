from fastapi import APIRouter, Depends, status

from movienight.api.deps import DbSession, get_current_user
from movienight.schemas.auth import MessageResponse
from movienight.schemas.proposal import CreateProposalRequest, ProposalResponse
from movienight.services.proposal_service import ProposalService

router = APIRouter(prefix="/proposals", tags=["proposals"])


@router.post(
    "",
    summary="Create screening proposal",
    description=(
        "Create a new movie screening proposal for "
        "a room and a fixed 2-hour time slot. "
        "The proposal is accepted only if it passes "
        "all scheduling and conflict validation rules."
    ),
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Proposal created successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "id": 12,
                        "room": "Room A",
                        "movie_title": "Interstellar",
                        "starts_at": "2026-04-06T18:00:00Z",
                        "ends_at": "2026-04-06T20:00:00Z",
                        "creator_id": 1,
                    }
                }
            },
        },
        400: {
            "description": "Proposal validation failed.",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_slot": {
                            "summary": "Invalid slot length",
                            "value": {
                                "detail": (
                                    "Proposal must last "
                                    "exactly 2 hours."
                                )
                            },
                        },
                        "invalid_start": {
                            "summary": "Invalid slot boundary",
                            "value": {
                                "detail": (
                                    "Proposal start time must match "
                                    "a 2-hour slot: 00:00, 02:00, 04:00, "
                                    "and so on."
                                )
                            },
                        },
                        "duplicate_overlap": {
                            "summary": "Same room + same movie overlap",
                            "value": {
                                "detail": (
                                    "An overlapping proposal "
                                    "for the same room and "
                                    "movie already exists."
                                )
                            },
                        },
                        "locked_conflict": {
                            "summary": "Conflict too close to start",
                            "value": {
                                "detail": (
                                    "A conflicting proposal cannot "
                                    "be created one hour or less "
                                    "before the start time."
                                )
                            },
                        },
                    }
                }
            },
        },
        401: {
            "description": "Authentication required.",
            "content": {
                "application/json": {
                    "example": {"detail": "Authentication required."}
                }
            },
        },
    },
)
def create_proposal(
    payload: CreateProposalRequest,
    db: DbSession,
    user=Depends(get_current_user),
) -> ProposalResponse:
    return ProposalService(db).create_proposal(
        payload=payload,
        current_user=user,
    )


@router.delete(
    "/{proposal_id}",
    summary="Delete own proposal",
    description=(
        "Delete the current user's proposal "
        "if deletion is still allowed."
    ),
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {"message": "Proposal deleted."}
                }
            }
        },
        400: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": (
                            "Past proposals cannot "
                            "be deleted."
                        )
                    }
                }
            }
        },
        403: {
            "content": {
                "application/json": {
                    "example": {
                        "detail": (
                            "You can delete only your "
                            "own proposals."
                        )
                    }
                }
            }
        },
        404: {
            "content": {
                "application/json": {
                    "example": {"detail": "Proposal not found."}
                }
            }
        },
    },
)
def delete_proposal(
    proposal_id: int,
    db: DbSession,
    user=Depends(get_current_user),
) -> MessageResponse:
    return ProposalService(db).delete_proposal(
        proposal_id=proposal_id,
        current_user=user
    )
