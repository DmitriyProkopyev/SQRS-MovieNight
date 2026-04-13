from datetime import datetime

from movienight.services.schedule_exceptions import raise_bad_request
from movienight.services.time_vote_lock import is_vote_locked


def ensure_not_locked_window_creation(
    starts_at: datetime,
    conflicts,
    now: datetime,
) -> None:
    del conflicts

    if is_vote_locked(starts_at, now):
        raise_bad_request(
            "New proposals should start later than an hour away."
        )
