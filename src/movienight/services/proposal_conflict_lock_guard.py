from datetime import datetime

from movienight.db.models import Proposal
from movienight.services.schedule_exceptions import raise_bad_request
from movienight.services.time_vote_lock import is_vote_locked


def ensure_not_locked_window_creation(
    starts_at: datetime,
    conflicts: list[Proposal],
    now: datetime,
) -> None:
    if conflicts and is_vote_locked(starts_at, now):
        raise_bad_request(
            "A conflicting proposal cannot be created one hour "
            "or less before the start time."
        )
