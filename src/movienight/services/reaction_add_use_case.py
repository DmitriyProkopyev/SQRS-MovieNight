from movienight.core.clock import utcnow
from movienight.db.models import FoodReaction
from movienight.services.reaction_context import build_reaction_context
from movienight.services.reaction_response_builder import (
    build_reaction_response,
)
from movienight.services.reaction_validation import (
    ensure_reaction_add_allowed,
)


def add_reaction_use_case(
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

    ensure_reaction_add_allowed(
        has_same_category=context["existing"] is not None,
        is_target=context["is_target"],
        proposal=context["proposal"],
        now=utcnow(),
    )

    reactions_repo.create(
        FoodReaction(
            user_id=current_user.id,
            proposal_id=proposal_id,
            category=context["normalized"],
            created_at=utcnow(),
        )
    )
    total = reactions_repo.count_for_proposal_and_category(
        proposal_id,
        context["normalized"],
    )

    return build_reaction_response(
        proposal_id=proposal_id,
        category=context["normalized"],
        total_for_category=total,
        message="Reaction added.",
    )
