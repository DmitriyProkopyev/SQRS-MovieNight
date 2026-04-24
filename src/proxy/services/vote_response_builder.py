from movienight.schemas.vote import VoteActionResponse


def build_vote_response(
    proposal_id: int,
    votes_count: int,
    message: str,
) -> VoteActionResponse:
    return VoteActionResponse(
        proposal_id=proposal_id,
        votes_count=votes_count,
        message=message,
    )
