from sqlalchemy.orm import Session

from proxy.repositories.proposals import ProposalRepository
from proxy.repositories.votes import VoteRepository
from movienight.schemas.vote import VoteActionResponse
from proxy.services.vote_add_use_case import add_vote_use_case
from proxy.services.vote_remove_use_case import (
    remove_vote_use_case,
)


class VoteService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.proposals = ProposalRepository(db)
        self.votes = VoteRepository(db)

    def add_vote(
        self,
        proposal_id: int,
        current_user,
    ) -> VoteActionResponse:
        return add_vote_use_case(
            proposals_repo=self.proposals,
            votes_repo=self.votes,
            proposal_id=proposal_id,
            current_user=current_user,
        )

    def remove_vote(
        self,
        proposal_id: int,
        current_user,
    ) -> VoteActionResponse:
        return remove_vote_use_case(
            proposals_repo=self.proposals,
            votes_repo=self.votes,
            proposal_id=proposal_id,
            current_user=current_user,
        )
