from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from movienight.db.models import Vote


class VoteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, vote: Vote) -> Vote:
        self.db.add(vote)
        self.db.commit()
        self.db.refresh(vote)
        return vote

    def exists_for_user_and_proposal(
        self,
        user_id: int,
        proposal_id: int
    ) -> bool:
        statement = select(Vote.id).where(
            Vote.user_id == user_id,
            Vote.proposal_id == proposal_id
        )
        return self.db.scalar(statement) is not None

    def find_by_user_and_proposal(
        self,
        user_id: int,
        proposal_id: int
    ) -> Vote | None:
        statement = select(Vote).where(
            Vote.user_id == user_id,
            Vote.proposal_id == proposal_id
        )
        return self.db.scalar(statement)

    def delete(self, vote: Vote) -> None:
        self.db.execute(delete(Vote).where(Vote.id == vote.id))
        self.db.commit()

    def count_for_proposal(self, proposal_id: int) -> int:
        statement = select(
            func.count(Vote.id)
        ).where(
            Vote.proposal_id == proposal_id
        )
        return int(self.db.scalar(statement) or 0)

    def get_user_votes_in_group(
        self,
        user_id: int,
        proposal_ids: list[int]
    ) -> list[Vote]:
        if not proposal_ids:
            return []
        statement = select(Vote).where(
            Vote.user_id == user_id,
            Vote.proposal_id.in_(proposal_ids)
        )
        return list(self.db.scalars(statement).all())

    def count_by_proposal_ids(
        self,
        proposal_ids: list[int]
    ) -> dict[int, int]:
        if not proposal_ids:
            return {}
        statement = (
            select(
                Vote.proposal_id,
                func.count(Vote.id)
            ).where(
                Vote.proposal_id.in_(proposal_ids)
            ).group_by(
                Vote.proposal_id
            )
        )
        return {
            proposal_id: count for proposal_id,
            count in self.db.execute(statement).all()
        }
