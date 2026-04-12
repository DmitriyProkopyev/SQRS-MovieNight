from sqlalchemy.orm import Session

from movienight.db.models import Proposal


def create_proposal(
    db: Session,
    proposal: Proposal,
) -> Proposal:
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


def delete_proposal(
    db: Session,
    proposal: Proposal,
) -> None:
    db.delete(proposal)
    db.commit()
