from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from movienight.db.models import FoodReaction


class ReactionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, reaction: FoodReaction) -> FoodReaction:
        self.db.add(reaction)
        self.db.commit()
        self.db.refresh(reaction)
        return reaction

    def find_by_user_proposal_category(
        self,
        user_id: int,
        proposal_id: int,
        category: str,
    ) -> FoodReaction | None:
        statement = select(FoodReaction).where(
            FoodReaction.user_id == user_id,
            FoodReaction.proposal_id == proposal_id,
            FoodReaction.category == category,
        )
        return self.db.scalar(statement)

    def delete(self, reaction: FoodReaction) -> None:
        self.db.execute(
            delete(FoodReaction).where(
                FoodReaction.id == reaction.id
            )
        )
        self.db.commit()

    def count_for_proposal_and_category(
        self, proposal_id: int,
        category: str
    ) -> int:
        statement = select(func.count(FoodReaction.id)).where(
            FoodReaction.proposal_id == proposal_id,
            FoodReaction.category == category,
        )
        return int(self.db.scalar(statement) or 0)

    def counts_for_proposal_ids(
        self,
        proposal_ids: list[int]
    ) -> dict[int, dict[str, int]]:
        if not proposal_ids:
            return {}
        statement = (
            select(
                FoodReaction.proposal_id,
                FoodReaction.category,
                func.count(FoodReaction.id)
            )
            .where(
                FoodReaction.proposal_id.in_(proposal_ids)
            )
            .group_by(
                FoodReaction.proposal_id,
                FoodReaction.category
            )
        )
        data: dict[int, dict[str, int]] = {}
        for proposal_id, category, count in self.db.execute(statement).all():
            data.setdefault(proposal_id, {})[str(category)] = count
        return data

    def user_categories_for_proposal_ids(
        self,
        user_id: int,
        proposal_ids: list[int]
    ) -> dict[int, list[str]]:
        if not proposal_ids:
            return {}
        statement = select(FoodReaction).where(
            FoodReaction.user_id == user_id,
            FoodReaction.proposal_id.in_(proposal_ids),
        )
        data: dict[int, list[str]] = {}
        for item in self.db.scalars(statement).all():
            data.setdefault(
                item.proposal_id,
                []
            ).append(str(item.category))
        return data
