from movienight.schemas.auth import MessageResponse
from movienight.schemas.proposal import CreateProposalRequest, ProposalResponse


class ProposalService:
    def __init__(self, db) -> None:
        self.db = db

    def create_proposal(
        self,
        payload: CreateProposalRequest,
        current_user,
    ) -> ProposalResponse:
        data = self.db.create_proposal(
            payload=payload.model_dump(mode="json"),
            current_user_id=current_user.id,
        )
        return ProposalResponse.model_validate(data)

    def delete_proposal(
        self,
        proposal_id: int,
        current_user,
    ) -> MessageResponse:
        data = self.db.delete_proposal(
            proposal_id=proposal_id,
            current_user_id=current_user.id,
        )
        return MessageResponse.model_validate(data)