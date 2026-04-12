from sqlalchemy.orm import Session

from movienight.repositories.proposals import ProposalRepository
from movienight.schemas.auth import MessageResponse
from movienight.schemas.proposal import (
    CreateProposalRequest,
    ProposalResponse,
)
from movienight.services.proposal_create_use_case import (
    create_proposal_use_case,
)
from movienight.services.proposal_delete_use_case import (
    delete_proposal_use_case,
)


class ProposalService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.proposals = ProposalRepository(db)

    def create_proposal(
        self,
        payload: CreateProposalRequest,
        current_user,
    ) -> ProposalResponse:
        return create_proposal_use_case(
            proposals_repo=self.proposals,
            payload=payload,
            current_user=current_user,
        )

    def delete_proposal(
        self,
        proposal_id: int,
        current_user,
    ) -> MessageResponse:
        return delete_proposal_use_case(
            proposals_repo=self.proposals,
            proposal_id=proposal_id,
            current_user=current_user,
        )
