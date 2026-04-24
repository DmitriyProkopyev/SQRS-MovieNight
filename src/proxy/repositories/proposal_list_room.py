from sqlalchemy import select
from sqlalchemy.orm import Session

from proxy.db.models import Proposal
from proxy.repositories.proposal_list_order import (
    apply_proposal_order,
)


def list_proposals_by_room(
    db: Session,
    room: str,
) -> list[Proposal]:
    statement = apply_proposal_order(
        select(Proposal).where(Proposal.room == room)
    )
    return list(db.scalars(statement))
