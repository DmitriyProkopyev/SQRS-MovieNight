from movienight.schemas.auth import MessageResponse
from movienight.schemas.proposal import ProposalResponse


def build_created_proposal_response(proposal) -> ProposalResponse:
    return ProposalResponse.model_validate(proposal)


def build_deleted_proposal_response() -> MessageResponse:
    return MessageResponse(message="Proposal deleted.")
