from sqlalchemy.orm import Session

from movienight.db.models import Vote
from movienight.repositories.vote_aggregate import (
    count_by_proposal_ids,
    count_for_proposal,
)
from movienight.repositories.vote_lookup import (
    exists_for_user_and_proposal,
    find_by_user_and_proposal,
    get_user_votes_in_group,
)
from movienight.repositories.vote_write import (
    create_vote,
    delete_vote,
)


class VoteRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def exists_for_user_and_proposal(
        self,
        user_id: int,
        proposal_id: int,
    ) -> bool:
        return exists_for_user_and_proposal(
            db=self.db,
            user_id=user_id,
            proposal_id=proposal_id,
        )

    def find_by_user_and_proposal(
        self,
        user_id: int,
        proposal_id: int,
    ) -> Vote | None:
        return find_by_user_and_proposal(
            db=self.db,
            user_id=user_id,
            proposal_id=proposal_id,
        )

    def create(self, vote: Vote) -> None:
        create_vote(self.db, vote)

    def delete(self, vote: Vote) -> None:
        delete_vote(self.db, vote)

    def count_for_proposal(self, proposal_id: int) -> int:
        return count_for_proposal(
            db=self.db,
            proposal_id=proposal_id,
        )

    def get_user_votes_in_group(
        self,
        user_id: int,
        proposal_ids: list[int],
    ) -> list[Vote]:
        return get_user_votes_in_group(
            db=self.db,
            user_id=user_id,
            proposal_ids=proposal_ids,
        )

    def count_by_proposal_ids(
        self,
        proposal_ids: list[int],
    ) -> dict[int, int]:
        return count_by_proposal_ids(
            db=self.db,
            proposal_ids=proposal_ids,
        )
