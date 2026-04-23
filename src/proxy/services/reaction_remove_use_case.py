from movienight.core.clock import utcnow
from proxy.services.reaction_context import build_reaction_context
from proxy.services.reaction_delete_action import (
    delete_reaction_and_count,
)
from proxy.services.reaction_existing_required import (
    require_existing_reaction,
)
from proxy.services.reaction_response_builder import (
    build_reaction_response,
)
from proxy.services.reaction_validation import (
    ensure_reaction_delete_allowed,
)


def remove_reaction_use_case(
    proposals_repo,
    reactions_repo,
    votes_repo,
    proposal_id: int,
    category: str,
    current_user,
):
    context = build_reaction_context(
        proposals_repo=proposals_repo,
        reactions_repo=reactions_repo,
        votes_repo=votes_repo,
        proposal_id=proposal_id,
        category=category,
        current_user=current_user,
    )

    ensure_reaction_delete_allowed(
        has_reaction=context["existing"] is not None,
        is_target=context["is_target"],
        proposal=context["proposal"],
        now=utcnow(),
    )

    existing = require_existing_reaction(context["existing"])
    total = delete_reaction_and_count(
        reactions_repo=reactions_repo,
        reaction=existing,
        proposal_id=proposal_id,
        category=context["normalized"],
    )

    return build_reaction_response(
        proposal_id=proposal_id,
        category=context["normalized"],
        total_for_category=total,
        message="Reaction removed.",
    )
