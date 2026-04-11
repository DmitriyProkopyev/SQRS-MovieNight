from sqlalchemy import select
from sqlalchemy.orm import Session

from movienight.db.models import Proposal
from movienight.repositories.proposal_list_order import (
    apply_proposal_order,
)


def list_proposals_by_creator_id(
    db: Session,
    creator_id: int,
) -> list[Proposal]:
    statement = apply_proposal_order(
        select(Proposal).where(Proposal.creator_id == creator_id)
    )
    return list(db.scalars(statement))
