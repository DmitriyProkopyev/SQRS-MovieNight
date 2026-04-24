from sqlalchemy import select
from sqlalchemy.orm import Session

from proxy.db.models import Vote


def get_user_votes_in_group(
    db: Session,
    user_id: int,
    proposal_ids: list[int],
) -> list[Vote]:
    if not proposal_ids:
        return []

    statement = select(Vote).where(
        Vote.user_id == user_id,
        Vote.proposal_id.in_(proposal_ids),
    )
    return list(db.scalars(statement))
