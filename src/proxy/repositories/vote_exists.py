from sqlalchemy import select
from sqlalchemy.orm import Session

from proxy.db.models import Vote


def exists_for_user_and_proposal(
    db: Session,
    user_id: int,
    proposal_id: int,
) -> bool:
    statement = select(Vote.id).where(
        Vote.user_id == user_id,
        Vote.proposal_id == proposal_id,
    )
    return db.scalar(statement) is not None
