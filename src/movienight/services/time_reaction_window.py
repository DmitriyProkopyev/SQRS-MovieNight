from datetime import datetime

from movienight.services.time_vote_lock import is_vote_locked


def can_add_reactions(starts_at: datetime, now: datetime) -> bool:
    return not is_vote_locked(starts_at, now)


def should_show_reactions(starts_at: datetime, now: datetime) -> bool:
    return is_vote_locked(starts_at, now)
