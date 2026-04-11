from fastapi import HTTPException, status

from movienight.core.clock import utcnow
from movienight.services.proposal_deletion_validation import (
    ensure_deletion_allowed,
)
from movienight.services.proposal_response_builder import (
    build_deleted_proposal_response,
)


def delete_proposal_use_case(
    proposals_repo,
    proposal_id: int,
    current_user,
):
    proposal = proposals_repo.get(proposal_id)
    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposal not found.",
        )

    ensure_deletion_allowed(
        proposal=proposal,
        current_user_id=current_user.id,
        now=utcnow(),
    )
    proposals_repo.delete(proposal)
    return build_deleted_proposal_response()
