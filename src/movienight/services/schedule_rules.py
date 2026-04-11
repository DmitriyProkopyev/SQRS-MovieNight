from datetime import datetime, timedelta

from fastapi import HTTPException, status

from movienight.core.clock import as_utc
from movienight.db.models import Proposal

_LOCK_WINDOW = timedelta(hours=1)
_MAX_DURATION_HOURS = 4
_MAX_OVERLAPS = 5


def overlaps(
    start_a: datetime,
    end_a: datetime,
    start_b: datetime,
    end_b: datetime
) -> bool:
    start_a = as_utc(start_a)
    end_a = as_utc(end_a)
    start_b = as_utc(start_b)
    end_b = as_utc(end_b)
    return start_a < end_b and start_b < end_a


def is_in_past(point: datetime, now: datetime) -> bool:
    return as_utc(point) < as_utc(now)


def is_vote_locked(starts_at: datetime, now: datetime) -> bool:
    starts_at = as_utc(starts_at)
    now = as_utc(now)
    return starts_at <= now + _LOCK_WINDOW


def can_add_reactions(starts_at: datetime, now: datetime) -> bool:
    starts_at = as_utc(starts_at)
    now = as_utc(now)
    return starts_at > now + _LOCK_WINDOW


def should_show_reactions(starts_at: datetime, now: datetime) -> bool:
    starts_at = as_utc(starts_at)
    now = as_utc(now)
    return starts_at <= now + _LOCK_WINDOW


def validate_proposal_time_bounds(
    starts_at: datetime,
    ends_at: datetime,
    now: datetime
) -> None:
    starts_at = as_utc(starts_at)
    ends_at = as_utc(ends_at)
    now = as_utc(now)

    if is_in_past(starts_at, now):
        _raise_bad_request("Proposal start time cannot be in the past.")

    if ends_at <= starts_at:
        _raise_bad_request("Proposal end time must be later than start time.")

    duration = ends_at - starts_at
    if duration != timedelta(hours=2):
        _raise_bad_request("Proposal must last exactly 2 hours.")

    if (
        starts_at.minute != 0 or
        starts_at.second != 0 or
        starts_at.microsecond != 0 or
        starts_at.hour % 2 != 0
    ):
        _raise_bad_request(
            "Proposal start time must match a 2-hour "
            "slot: 00:00, 02:00, 04:00, and so on."
        )


def find_conflicts(
    target_room: str,
    starts_at: datetime,
    ends_at: datetime,
    proposals: list[Proposal],
) -> list[Proposal]:
    return [
        proposal
        for proposal in proposals
        if proposal.room == target_room and
        overlaps(
            starts_at,
            ends_at,
            proposal.starts_at,
            proposal.ends_at
        )
    ]


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
        existing_room_proposals
    )
    ensure_not_duplicate(
        room,
        movie_title,
        starts_at,
        ends_at,
        conflicts
    )
    ensure_not_too_many_conflicts(conflicts)
    ensure_not_locked_window_creation(
        starts_at,
        conflicts,
        now
    )


def ensure_not_duplicate(
    room: str,
    movie_title: str,
    starts_at: datetime,
    ends_at: datetime,
    conflicts: list[Proposal],
) -> None:
    normalized_title = movie_title.strip().lower()

    for proposal in conflicts:
        same_movie = proposal.movie_title.strip().lower() == normalized_title
        if proposal.room == room and same_movie and overlaps(
            starts_at,
            ends_at,
            proposal.starts_at,
            proposal.ends_at,
        ):
            _raise_bad_request(
                "An overlapping proposal for "
                "the same room and movie already exists."
            )


def ensure_not_too_many_conflicts(conflicts: list[Proposal]) -> None:
    if len(conflicts) >= _MAX_OVERLAPS:
        _raise_bad_request(
            "Too many overlapping proposals "
            "already exist in this room."
        )


def ensure_not_locked_window_creation(
    starts_at: datetime,
    conflicts: list[Proposal],
    now: datetime,
) -> None:
    if conflicts and is_vote_locked(starts_at, now):
        _raise_bad_request(
            "A conflicting proposal cannot "
            "be created one hour or less before the start time."
        )


def ensure_deletion_allowed(
    proposal: Proposal,
    current_user_id: int,
    now: datetime
) -> None:
    if proposal.creator_id != current_user_id:
        _raise_forbidden("You can delete only your own proposals.")
    if is_in_past(proposal.starts_at, now):
        _raise_bad_request("Past proposals cannot be deleted.")


def _raise_bad_request(message: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message
    )


def _raise_forbidden(message: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=message
    )
