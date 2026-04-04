from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from movienight.core.clock import utcnow
from movienight.db.models import FoodCategory, FoodReaction, User
from movienight.repositories.proposals import ProposalRepository
from movienight.repositories.reactions import ReactionRepository
from movienight.repositories.votes import VoteRepository
from movienight.schemas.reaction import ReactionActionResponse
from movienight.services.voting_rules import (
    build_conflict_component,
    ensure_reaction_add_allowed,
    ensure_reaction_delete_allowed,
    is_reaction_target,
)


class ReactionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.proposals = ProposalRepository(db)
        self.reactions = ReactionRepository(db)
        self.votes = VoteRepository(db)

    def add_reaction(self, proposal_id: int, category: str, current_user: User) -> ReactionActionResponse:
        proposal = self._require_proposal(proposal_id)
        normalized = self._normalize_category(category)
        existing = self.reactions.find_by_user_proposal_category(current_user.id, proposal_id, normalized)

        is_target = self._is_reaction_target(proposal)

        ensure_reaction_add_allowed(
            has_same_category=existing is not None,
            is_target=is_target,
            proposal=proposal,
            now=utcnow(),
        )

        self.reactions.create(
            FoodReaction(
                user_id=current_user.id,
                proposal_id=proposal_id,
                category=FoodCategory(normalized),
                created_at=utcnow(),
            )
        )
        total = self.reactions.count_for_proposal_and_category(proposal_id, normalized)
        return ReactionActionResponse(
            proposal_id=proposal_id,
            category=normalized,
            total_for_category=total,
            message="Reaction added.",
        )

    def remove_reaction(self, proposal_id: int, category: str, current_user: User) -> ReactionActionResponse:
        proposal = self._require_proposal(proposal_id)
        normalized = self._normalize_category(category)
        existing = self.reactions.find_by_user_proposal_category(current_user.id, proposal_id, normalized)

        is_target = self._is_reaction_target(proposal)

        ensure_reaction_delete_allowed(
            has_reaction=existing is not None,
            is_target=is_target,
            proposal=proposal,
            now=utcnow(),
        )

        assert existing is not None
        self.reactions.delete(existing)
        total = self.reactions.count_for_proposal_and_category(proposal_id, normalized)
        return ReactionActionResponse(
            proposal_id=proposal_id,
            category=normalized,
            total_for_category=total,
            message="Reaction removed.",
        )

    def _is_reaction_target(self, proposal) -> bool:
        room_proposals = self.proposals.list_by_room(proposal.room)
        component = build_conflict_component(proposal, room_proposals)
        vote_counts = self.votes.count_by_proposal_ids([item.id for item in component])
        return is_reaction_target(
            proposal=proposal,
            component=component,
            vote_counts=vote_counts,
            now=utcnow(),
        )

    def _require_proposal(self, proposal_id: int):
        proposal = self.proposals.get(proposal_id)
        if proposal is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found.")
        return proposal

    def _normalize_category(self, category: str) -> str:
        value = category.strip().lower()
        try:
            return FoodCategory(value).value
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown food reaction category.",
            ) from exc