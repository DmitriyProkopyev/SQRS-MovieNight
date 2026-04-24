from fastapi import HTTPException, status


def require_vote(
    votes_repo,
    user_id: int,
    proposal_id: int,
):
    vote = votes_repo.find_by_user_and_proposal(user_id, proposal_id)
    if vote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote not found.",
        )
    return vote
