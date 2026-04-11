from sqlalchemy import select
from sqlalchemy.orm import Session

from movienight.db.models import Proposal
from movienight.repositories.proposal_list_order import (
    apply_proposal_order,
)


def list_all_proposals(
    db: Session,
) -> list[Proposal]:
    statement = apply_proposal_order(select(Proposal))
    return list(db.scalars(statement))
