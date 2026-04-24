from sqlalchemy import func, select
from sqlalchemy.orm import Session

from proxy.db.models import FoodReaction


def count_for_proposal_and_category(
    db: Session,
    proposal_id: int,
    category: str,
) -> int:
    statement = select(func.count(FoodReaction.id)).where(
        FoodReaction.proposal_id == proposal_id,
        FoodReaction.category == category,
    )
    return int(db.scalar(statement) or 0)
