from sqlalchemy.orm import Session

from movienight.db.models import FoodReaction
from movienight.repositories.reaction_aggregate import (
    count_for_proposal_and_category,
    counts_for_proposal_ids,
)
from movienight.repositories.reaction_lookup import (
    find_by_user_proposal_category,
    user_categories_for_proposal_ids,
)
from movienight.repositories.reaction_write import (
    create_reaction,
    delete_reaction,
)


class ReactionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_by_user_proposal_category(
        self,
        user_id: int,
        proposal_id: int,
        category: str,
    ) -> FoodReaction | None:
        return find_by_user_proposal_category(
            db=self.db,
            user_id=user_id,
            proposal_id=proposal_id,
            category=category,
        )

    def create(self, reaction: FoodReaction) -> None:
        create_reaction(self.db, reaction)

    def delete(self, reaction: FoodReaction) -> None:
        delete_reaction(self.db, reaction)

    def count_for_proposal_and_category(
        self,
        proposal_id: int,
        category: str,
    ) -> int:
        return count_for_proposal_and_category(
            db=self.db,
            proposal_id=proposal_id,
            category=category,
        )

    def counts_for_proposal_ids(
        self,
        proposal_ids: list[int],
    ) -> dict[int, dict[str, int]]:
        return counts_for_proposal_ids(
            db=self.db,
            proposal_ids=proposal_ids,
        )

    def user_categories_for_proposal_ids(
        self,
        user_id: int,
        proposal_ids: list[int],
    ) -> dict[int, list[str]]:
        return user_categories_for_proposal_ids(
            db=self.db,
            user_id=user_id,
            proposal_ids=proposal_ids,
        )
