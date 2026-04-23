from fastapi import APIRouter, HTTPException, status

from proxy.api.deps import DbSession
from proxy.api.models import InternalReactionRequest
from proxy.repositories.users import UserRepository
from proxy.services.reaction_service import ReactionService

router = APIRouter()


@router.post("/add", status_code=status.HTTP_201_CREATED)
def add_reaction(payload: InternalReactionRequest, db: DbSession):
    current_user = UserRepository(db).get_by_id(payload.current_user_id)
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return ReactionService(db).add_reaction(
        proposal_id=payload.proposal_id,
        category=payload.category,
        current_user=current_user,
    )


@router.post("/remove")
def remove_reaction(payload: InternalReactionRequest, db: DbSession):
    current_user = UserRepository(db).get_by_id(payload.current_user_id)
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return ReactionService(db).remove_reaction(
        proposal_id=payload.proposal_id,
        category=payload.category,
        current_user=current_user,
    )