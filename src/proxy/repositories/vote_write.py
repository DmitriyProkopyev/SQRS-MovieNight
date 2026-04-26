from sqlalchemy import delete
from sqlalchemy.orm import Session

from proxy.db.models import Vote


def create_vote(
    db: Session,
    vote: Vote,
) -> None:
    db.add(vote)
    db.commit()


def delete_vote(
    db: Session,
    vote: Vote,
) -> None:
    db.execute(
        delete(Vote).where(
            Vote.id == vote.id,
        )
    )
    db.commit()
