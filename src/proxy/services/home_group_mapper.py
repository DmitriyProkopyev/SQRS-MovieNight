from datetime import datetime

from proxy.services.home_group_cards import build_group_cards
from proxy.services.home_group_context import build_group_context
from proxy.services.home_group_response_builder import (
    build_proposal_group,
)


def map_group(
    component,
    vote_counts: dict[int, int],
    reaction_counts: dict[int, dict[str, int]],
    my_reactions_map: dict[int, list[str]],
    my_votes: set[int],
    current_user,
    now: datetime,
):
    context = build_group_context(
        component=component,
        vote_counts=vote_counts,
        now=now,
    )
    cards = build_group_cards(
        component=component,
        component_vote_counts=context["component_vote_counts"],
        vote_counts=vote_counts,
        reaction_counts=reaction_counts,
        my_reactions_map=my_reactions_map,
        my_votes=my_votes,
        current_user=current_user,
        now=now,
        winner_id=context["winner_id"],
    )

    return build_proposal_group(
        component=component,
        starts_at=context["starts_at"],
        ends_at=context["ends_at"],
        winner_id=context["winner_id"],
        cards=cards,
        now=now,
    )
