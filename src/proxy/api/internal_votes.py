from fastapi import APIRouter, HTTPException, status

from proxy.api.deps import DbSession
from proxy.api.models import InternalVoteRequest
from proxy.repositories.users import UserRepository
from proxy.services.vote_service import VoteService

router = APIRouter()


@router.post("/add", status_code=status.HTTP_201_CREATED)
def add_vote(payload: InternalVoteRequest, db: DbSession):
    current_user = UserRepository(db).get_by_id(payload.current_user_id)
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return VoteService(db).add_vote(
        proposal_id=payload.proposal_id,
        current_user=current_user,
    )


@router.post("/remove")
def remove_vote(payload: InternalVoteRequest, db: DbSession):
    current_user = UserRepository(db).get_by_id(payload.current_user_id)
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return VoteService(db).remove_vote(
        proposal_id=payload.proposal_id,
        current_user=current_user,
    )