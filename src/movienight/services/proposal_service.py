from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from movienight.core.clock import utcnow
from movienight.db.models import Proposal, User
from movienight.repositories.proposals import ProposalRepository
from movienight.schemas.auth import MessageResponse
from movienight.schemas.proposal import CreateProposalRequest, ProposalResponse
from movienight.services.schedule_rules import (
    ensure_creation_allowed,
    ensure_deletion_allowed,
    validate_proposal_time_bounds,
)


class ProposalService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.proposals = ProposalRepository(db)

    def create_proposal(
        self,
        payload: CreateProposalRequest,
        current_user: User
    ) -> ProposalResponse:
        now = utcnow()
        validate_proposal_time_bounds(
            payload.starts_at,
            payload.ends_at,
            now
        )
        room_proposals = self.proposals.list_by_room(payload.room)
        ensure_creation_allowed(
            room=payload.room,
            movie_title=payload.movie_title,
            starts_at=payload.starts_at,
            ends_at=payload.ends_at,
            existing_room_proposals=room_proposals,
            now=now,
        )

        proposal = Proposal(
            creator_id=current_user.id,
            room=payload.room,
            movie_title=payload.movie_title,
            starts_at=payload.starts_at,
            ends_at=payload.ends_at,
            created_at=now,
        )
        created = self.proposals.create(proposal)
        return ProposalResponse.model_validate(created)

    def delete_proposal(
        self,
        proposal_id: int,
        current_user: User
    ) -> MessageResponse:
        proposal = self.proposals.get(proposal_id)
        if proposal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proposal not found."
            )
        ensure_deletion_allowed(proposal, current_user.id, utcnow())
        self.proposals.delete(proposal)
        return MessageResponse(message=f"Proposal {proposal_id} was deleted.")
