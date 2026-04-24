from sqlalchemy.orm import Session

from proxy.db.models import User
from proxy.repositories.proposals import ProposalRepository
from proxy.repositories.reactions import ReactionRepository
from proxy.repositories.votes import VoteRepository
from movienight.schemas.reaction import ReactionActionResponse
from proxy.services.reaction_add_use_case import (
    add_reaction_use_case,
)
from proxy.services.reaction_remove_use_case import (
    remove_reaction_use_case,
)


class ReactionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.proposals = ProposalRepository(db)
        self.reactions = ReactionRepository(db)
        self.votes = VoteRepository(db)

    def add_reaction(
        self,
        proposal_id: int,
        category: str,
        current_user: User,
    ) -> ReactionActionResponse:
        return add_reaction_use_case(
            proposals_repo=self.proposals,
            reactions_repo=self.reactions,
            votes_repo=self.votes,
            proposal_id=proposal_id,
            category=category,
            current_user=current_user,
        )

    def remove_reaction(
        self,
        proposal_id: int,
        category: str,
        current_user: User,
    ) -> ReactionActionResponse:
        return remove_reaction_use_case(
            proposals_repo=self.proposals,
            reactions_repo=self.reactions,
            votes_repo=self.votes,
            proposal_id=proposal_id,
            category=category,
            current_user=current_user,
        )
