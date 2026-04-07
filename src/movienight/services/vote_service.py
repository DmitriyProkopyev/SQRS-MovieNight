from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from movienight.core.clock import utcnow
from movienight.db.models import User, Vote
from movienight.repositories.proposals import ProposalRepository
from movienight.repositories.votes import VoteRepository
from movienight.schemas.vote import VoteActionResponse
from movienight.services.voting_rules import build_conflict_component, ensure_vote_allowed, ensure_vote_removal_allowed


class VoteService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.proposals = ProposalRepository(db)
        self.votes = VoteRepository(db)

    def add_vote(self, proposal_id: int, current_user: User) -> VoteActionResponse:
        proposal = self._require_proposal(proposal_id)
        component = build_conflict_component(proposal, self.proposals.list_by_room(proposal.room))
        component_ids = [item.id for item in component]
        user_votes = self.votes.get_user_votes_in_group(current_user.id, component_ids)
        already_voted_for_target = self.votes.exists_for_user_and_proposal(current_user.id, proposal_id)
        ensure_vote_allowed(
            proposal=proposal,
            current_user_id=current_user.id,
            user_votes_in_group=[item.proposal_id for item in user_votes],
            already_voted_for_target=already_voted_for_target,
            now=utcnow(),
        )
        self.votes.create(Vote(user_id=current_user.id, proposal_id=proposal_id, created_at=utcnow()))
        count = self.votes.count_for_proposal(proposal_id)
        return VoteActionResponse(proposal_id=proposal_id, votes_count=count, message="Vote added.")

    def remove_vote(self, proposal_id: int, current_user: User) -> VoteActionResponse:
        proposal = self._require_proposal(proposal_id)
        vote = self.votes.find_by_user_and_proposal(current_user.id, proposal_id)
        ensure_vote_removal_allowed(has_vote=vote is not None, proposal=proposal, now=utcnow())
        assert vote is not None
        self.votes.delete(vote)
        count = self.votes.count_for_proposal(proposal_id)
        return VoteActionResponse(proposal_id=proposal_id, votes_count=count, message="Vote removed.")

    def _require_proposal(self, proposal_id: int):
        proposal = self.proposals.get(proposal_id)
        if proposal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found.")
        return proposal
