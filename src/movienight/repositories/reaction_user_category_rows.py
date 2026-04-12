from sqlalchemy import select
from sqlalchemy.orm import Session

from movienight.db.models import FoodReaction


def load_user_category_rows(
    db: Session,
    user_id: int,
    proposal_ids: list[int],
):
    if not proposal_ids:
        return []

    statement = select(
        FoodReaction.proposal_id,
        FoodReaction.category,
    ).where(
        FoodReaction.user_id == user_id,
        FoodReaction.proposal_id.in_(proposal_ids),
    )
    return db.execute(statement).all()
