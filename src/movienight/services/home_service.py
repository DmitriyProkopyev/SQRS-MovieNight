from sqlalchemy.orm import Session

from movienight.core.clock import utcnow
from movienight.db.models import User
from movienight.repositories.proposals import ProposalRepository
from movienight.repositories.reactions import ReactionRepository
from movienight.repositories.votes import VoteRepository
from movienight.schemas.home import HomePageResponse
from movienight.services.home_group_builder import build_home_groups


class HomeService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.proposals = ProposalRepository(db)
        self.votes = VoteRepository(db)
        self.reactions = ReactionRepository(db)

    def get_home_page(
        self,
        current_user: User,
        mine_only: bool = False,
    ) -> HomePageResponse:
        proposals = self.load_proposals(
            current_user=current_user,
            mine_only=mine_only,
        )
        proposal_ids = [item.id for item in proposals]
        now = utcnow()

        vote_counts = self.votes.count_by_proposal_ids(proposal_ids)
        reaction_counts = self.reactions.counts_for_proposal_ids(proposal_ids)
        my_reactions_map = self.reactions.user_categories_for_proposal_ids(
            current_user.id,
            proposal_ids,
        )
        my_votes = {
            item.proposal_id
            for item in self.votes.get_user_votes_in_group(
                current_user.id,
                proposal_ids,
            )
        }

        return HomePageResponse(
            groups=build_home_groups(
                proposals=proposals,
                vote_counts=vote_counts,
                reaction_counts=reaction_counts,
                my_reactions_map=my_reactions_map,
                my_votes=my_votes,
                current_user=current_user,
                now=now,
            )
        )

    def load_proposals(
        self,
        current_user: User,
        mine_only: bool,
    ):
        if mine_only:
            return self.proposals.list_by_creator_id(current_user.id)
        return self.proposals.list_all()
