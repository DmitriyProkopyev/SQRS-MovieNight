from datetime import datetime

from movienight.db.models import Proposal
from movienight.services.home_reaction_permissions import (
    build_reaction_permissions,
)
from movienight.services.home_reaction_target import (
    is_reaction_block_active,
)
from movienight.services.home_reaction_visibility import (
    build_visible_reactions,
)


def build_reaction_state(
    proposal: Proposal,
    component: list[Proposal],
    component_vote_counts: dict[int, int],
    reactions: dict[str, int],
    my_reactions: list[str],
    now: datetime,
) -> dict:
    reaction_block_active = is_reaction_block_active(
        proposal=proposal,
        component=component,
        component_vote_counts=component_vote_counts,
        now=now,
    )
    visible = build_visible_reactions(
        reaction_block_active=reaction_block_active,
        reactions=reactions,
        my_reactions=my_reactions,
    )
    permissions = build_reaction_permissions(
        reaction_block_active=reaction_block_active,
        my_reactions=my_reactions,
    )

    return {
        "reaction_block_active": reaction_block_active,
        **visible,
        **permissions,
    }
