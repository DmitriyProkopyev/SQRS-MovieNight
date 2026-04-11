from datetime import datetime

from movienight.db.models import Proposal
from movienight.services.proposal_conflict_duplicate import (
    ensure_not_duplicate,
)
from movienight.services.proposal_conflict_limits import (
    ensure_not_too_many_conflicts,
)
from movienight.services.proposal_conflict_lock_guard import (
    ensure_not_locked_window_creation,
)
from movienight.services.proposal_conflict_lookup import find_conflicts


def ensure_creation_allowed(
    room: str,
    movie_title: str,
    starts_at: datetime,
    ends_at: datetime,
    existing_room_proposals: list[Proposal],
    now: datetime,
) -> None:
    conflicts = find_conflicts(
        room,
        starts_at,
        ends_at,
        existing_room_proposals,
    )
    ensure_not_duplicate(
        room=room,
        movie_title=movie_title,
        starts_at=starts_at,
        ends_at=ends_at,
        conflicts=conflicts,
    )
    ensure_not_too_many_conflicts(conflicts)
    ensure_not_locked_window_creation(
        starts_at=starts_at,
        conflicts=conflicts,
        now=now,
    )
