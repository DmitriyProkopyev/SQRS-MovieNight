from sqlalchemy import func, select
from sqlalchemy.orm import Session

from movienight.db.models import Vote


def load_vote_count_rows(
    db: Session,
    proposal_ids: list[int],
):
    if not proposal_ids:
        return []

    statement = select(
        Vote.proposal_id,
        func.count(Vote.id),
    ).where(
        Vote.proposal_id.in_(proposal_ids),
    ).group_by(
        Vote.proposal_id,
    )
    return db.execute(statement).all()
