from movienight.services.reaction_window_check import (
    is_reaction_window_open,
)
from movienight.services.reaction_winner_target import (
    matches_reaction_target,
)


def is_reaction_target(
    proposal,
    component,
    vote_counts: dict[int, int],
    now,
) -> bool:
    if not is_reaction_window_open(proposal, now):
        return False

    return matches_reaction_target(
        proposal=proposal,
        component=component,
        vote_counts=vote_counts,
    )
