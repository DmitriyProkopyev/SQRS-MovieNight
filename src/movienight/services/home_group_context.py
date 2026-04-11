from datetime import datetime

from movienight.services.home_component_vote_counts import (
    build_component_vote_counts,
)
from movienight.services.home_group_window import build_group_window
from movienight.services.home_group_winner import build_winner_id
from movienight.services.voting_rules import choose_winner


def build_group_context(
    component,
    vote_counts: dict[int, int],
    now: datetime,
) -> dict:
    winner = choose_winner(component, vote_counts) if component else None
    winner_id = build_winner_id(
        component=component,
        winner=winner,
        now=now,
    )
    starts_at, ends_at = build_group_window(component)
    component_vote_counts = build_component_vote_counts(
        component,
        vote_counts,
    )

    return {
        "winner_id": winner_id,
        "starts_at": starts_at,
        "ends_at": ends_at,
        "component_vote_counts": component_vote_counts,
    }
