from movienight.schemas.reaction import ReactionActionResponse


class ReactionService:
    def __init__(self, db) -> None:
        self.db = db

    def add_reaction(
        self,
        proposal_id: int,
        category: str,
        current_user,
    ) -> ReactionActionResponse:
        data = self.db.add_reaction(
            proposal_id=proposal_id,
            category=category,
            current_user_id=current_user.id,
        )
        return ReactionActionResponse.model_validate(data)

    def remove_reaction(
        self,
        proposal_id: int,
        category: str,
        current_user,
    ) -> ReactionActionResponse:
        data = self.db.remove_reaction(
            proposal_id=proposal_id,
            category=category,
            current_user_id=current_user.id,
        )
        return ReactionActionResponse.model_validate(data)