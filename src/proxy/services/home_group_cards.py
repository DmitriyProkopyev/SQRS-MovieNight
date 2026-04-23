from datetime import datetime

from proxy.db.models import Proposal, User
from proxy.services.home_card_mapper import map_card


def build_group_cards(
    component: list[Proposal],
    component_vote_counts: dict[int, int],
    vote_counts: dict[int, int],
    reaction_counts: dict[int, dict[str, int]],
    my_reactions_map: dict[int, list[str]],
    my_votes: set[int],
    current_user: User,
    now: datetime,
    winner_id: int | None,
):
    return [
        map_card(
            proposal=item,
            component=component,
            component_vote_counts=component_vote_counts,
            votes_count=vote_counts.get(item.id, 0),
            my_vote=item.id in my_votes,
            reactions=reaction_counts.get(item.id, {}),
            my_reactions=my_reactions_map.get(item.id, []),
            current_user=current_user,
            now=now,
            winner_id=winner_id,
        )
        for item in component
    ]
