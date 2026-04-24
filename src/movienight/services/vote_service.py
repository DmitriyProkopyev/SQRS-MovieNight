from movienight.schemas.vote import VoteActionResponse


class VoteService:
    def __init__(self, db) -> None:
        self.db = db

    def add_vote(
        self,
        proposal_id: int,
        current_user,
    ) -> VoteActionResponse:
        data = self.db.add_vote(
            proposal_id=proposal_id,
            current_user_id=current_user.id,
        )
        return VoteActionResponse.model_validate(data)

    def remove_vote(
        self,
        proposal_id: int,
        current_user,
    ) -> VoteActionResponse:
        data = self.db.remove_vote(
            proposal_id=proposal_id,
            current_user_id=current_user.id,
        )
        return VoteActionResponse.model_validate(data)