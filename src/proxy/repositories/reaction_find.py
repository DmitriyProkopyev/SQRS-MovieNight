from sqlalchemy import select
from sqlalchemy.orm import Session

from proxy.db.models import FoodReaction


def find_by_user_proposal_category(
    db: Session,
    user_id: int,
    proposal_id: int,
    category: str,
) -> FoodReaction | None:
    statement = select(FoodReaction).where(
        FoodReaction.user_id == user_id,
        FoodReaction.proposal_id == proposal_id,
        FoodReaction.category == category,
    )
    return db.scalar(statement)
