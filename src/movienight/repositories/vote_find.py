from sqlalchemy import select
from sqlalchemy.orm import Session

from movienight.db.models import Vote


def find_by_user_and_proposal(
    db: Session,
    user_id: int,
    proposal_id: int,
) -> Vote | None:
    statement = select(Vote).where(
        Vote.user_id == user_id,
        Vote.proposal_id == proposal_id,
    )
    return db.scalar(statement)
