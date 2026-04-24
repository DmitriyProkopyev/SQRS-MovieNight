from sqlalchemy import func, select
from sqlalchemy.orm import Session

from proxy.db.models import FoodReaction


def load_reaction_count_rows(
    db: Session,
    proposal_ids: list[int],
):
    if not proposal_ids:
        return []

    statement = select(
        FoodReaction.proposal_id,
        FoodReaction.category,
        func.count(FoodReaction.id),
    ).where(
        FoodReaction.proposal_id.in_(proposal_ids),
    ).group_by(
        FoodReaction.proposal_id,
        FoodReaction.category,
    )
    return db.execute(statement).all()
