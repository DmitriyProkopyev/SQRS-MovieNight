from fastapi import APIRouter, HTTPException, status

from proxy.api.deps import DbSession
from proxy.api.models import InternalProposalCreateRequest, InternalProposalDeleteRequest
from proxy.repositories.users import UserRepository
from proxy.services.proposal_service import ProposalService

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_proposal(payload: InternalProposalCreateRequest, db: DbSession):
    current_user = UserRepository(db).get_by_id(payload.current_user_id)
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return ProposalService(db).create_proposal(
        payload=payload.payload,
        current_user=current_user,
    )


@router.post("/delete")
def delete_proposal(payload: InternalProposalDeleteRequest, db: DbSession):
    current_user = UserRepository(db).get_by_id(payload.current_user_id)
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return ProposalService(db).delete_proposal(
        proposal_id=payload.proposal_id,
        current_user=current_user,
    )