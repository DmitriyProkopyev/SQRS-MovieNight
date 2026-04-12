from movienight.services.home_group_window import build_group_window
from movienight.services.schedule_rules import is_vote_locked


def should_show_winner(
    component,
    now,
) -> bool:
    starts_at, _ = build_group_window(component)
    return len(component) > 1 and is_vote_locked(starts_at, now)
