from sqlalchemy import select
from sqlalchemy.orm import Session

from movienight.db.models import Proposal


def get_proposal(
    db: Session,
    proposal_id: int,
) -> Proposal | None:
    statement = select(Proposal).where(Proposal.id == proposal_id)
    return db.scalar(statement)
