from sqlalchemy.orm import Session

from movienight.db.models import Proposal
from movienight.repositories.proposal_lookup import (
    get_proposal,
    list_all_proposals,
    list_proposals_by_creator_id,
    list_proposals_by_room,
)
from movienight.repositories.proposal_write import (
    create_proposal,
    delete_proposal,
)


class ProposalRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, proposal_id: int) -> Proposal | None:
        return get_proposal(self.db, proposal_id)

    def create(self, proposal: Proposal) -> Proposal:
        return create_proposal(self.db, proposal)

    def delete(self, proposal: Proposal) -> None:
        delete_proposal(self.db, proposal)

    def list_all(self) -> list[Proposal]:
        return list_all_proposals(self.db)

    def list_by_room(self, room: str) -> list[Proposal]:
        return list_proposals_by_room(self.db, room)

    def list_by_creator_id(
        self,
        creator_id: int,
    ) -> list[Proposal]:
        return list_proposals_by_creator_id(self.db, creator_id)
