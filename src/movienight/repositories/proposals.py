from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from movienight.db.models import Proposal


class ProposalRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, proposal: Proposal) -> Proposal:
        self.db.add(proposal)
        self.db.commit()
        self.db.refresh(proposal)
        return proposal

    def get(self, proposal_id: int) -> Proposal | None:
        return self.db.get(Proposal, proposal_id)

    def list_all(self) -> list[Proposal]:
        statement = select(Proposal).order_by(
            Proposal.starts_at,
            Proposal.created_at
        )
        return list(self.db.scalars(statement).all())

    def list_by_room(self, room: str) -> list[Proposal]:
        statement = (
            select(Proposal)
            .where(Proposal.room == room)
            .order_by(
                Proposal.starts_at,
                Proposal.created_at
            )
        )
        return list(self.db.scalars(statement).all())

    def delete(self, proposal: Proposal) -> None:
        self.db.execute(
            delete(Proposal).where(
                Proposal.id == proposal.id
            )
        )
        self.db.commit()

    def list_by_creator_id(self, creator_id: int) -> list[Proposal]:
        statement = (
            select(Proposal)
            .options(joinedload(Proposal.creator))
            .where(Proposal.creator_id == creator_id)
            .order_by(
                Proposal.starts_at,
                Proposal.created_at,
                Proposal.id
            )
        )
        return list(self.db.scalars(statement))
