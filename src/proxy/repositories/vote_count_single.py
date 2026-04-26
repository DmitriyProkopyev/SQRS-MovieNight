from sqlalchemy import func, select
from sqlalchemy.orm import Session

from proxy.db.models import Vote


def count_for_proposal(
    db: Session,
    proposal_id: int,
) -> int:
    statement = select(func.count(Vote.id)).where(
        Vote.proposal_id == proposal_id,
    )
    return int(db.scalar(statement) or 0)
