from fastapi import HTTPException, status


def require_proposal(proposals_repo, proposal_id: int):
    proposal = proposals_repo.get(proposal_id)
    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found.",
        )
    return proposal
