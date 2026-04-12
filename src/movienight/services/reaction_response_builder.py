from movienight.schemas.reaction import ReactionActionResponse


def build_reaction_response(
    proposal_id: int,
    category: str,
    total_for_category: int,
    message: str,
) -> ReactionActionResponse:
    return ReactionActionResponse(
        proposal_id=proposal_id,
        category=category,
        total_for_category=total_for_category,
        message=message,
    )
