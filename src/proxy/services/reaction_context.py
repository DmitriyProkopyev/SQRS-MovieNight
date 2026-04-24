from proxy.services.reaction_category import normalize_category
from proxy.services.reaction_proposal_loader import require_proposal
from proxy.services.reaction_target_service import (
    is_valid_reaction_target,
)


def build_reaction_context(
    proposals_repo,
    reactions_repo,
    votes_repo,
    proposal_id: int,
    category: str,
    current_user,
) -> dict:
    proposal = require_proposal(proposals_repo, proposal_id)
    normalized = normalize_category(category)
    existing = reactions_repo.find_by_user_proposal_category(
        current_user.id,
        proposal_id,
        normalized,
    )
    is_target = is_valid_reaction_target(
        proposal=proposal,
        proposals_repo=proposals_repo,
        votes_repo=votes_repo,
    )

    return {
        "proposal": proposal,
        "normalized": normalized,
        "existing": existing,
        "is_target": is_target,
    }
