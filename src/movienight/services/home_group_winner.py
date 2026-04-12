from movienight.services.home_group_winner_visibility import (
    should_show_winner,
)


def build_winner_id(
    component,
    winner,
    now,
) -> int | None:
    if winner is None:
        return None

    if should_show_winner(component, now):
        return winner.id

    return None
