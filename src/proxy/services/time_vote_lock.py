from datetime import datetime, timedelta

from movienight.core.clock import as_utc

_LOCK_WINDOW = timedelta(hours=1)


def is_vote_locked(starts_at: datetime, now: datetime) -> bool:
    starts_at = as_utc(starts_at)
    now = as_utc(now)
    return starts_at <= now + _LOCK_WINDOW
