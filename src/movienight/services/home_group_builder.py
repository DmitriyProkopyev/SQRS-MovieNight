from datetime import datetime

from movienight.services.home_group_accumulator import (
    accumulate_home_groups,
)
from movienight.services.home_group_sorter import sort_home_groups


def build_home_groups(
    proposals,
    vote_counts: dict[int, int],
    reaction_counts: dict[int, dict[str, int]],
    my_reactions_map: dict[int, list[str]],
    my_votes: set[int],
    current_user,
    now: datetime,
):
    groups = accumulate_home_groups(
        proposals=proposals,
        vote_counts=vote_counts,
        reaction_counts=reaction_counts,
        my_reactions_map=my_reactions_map,
        my_votes=my_votes,
        current_user=current_user,
        now=now,
    )
    return sort_home_groups(groups)
