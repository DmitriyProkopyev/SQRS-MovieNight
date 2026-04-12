from movienight.core.clock import utcnow
from movienight.schemas.schedule import ScheduleSlot
from movienight.services.schedule_time_rules import (
    is_in_past,
    is_vote_locked,
)


def map_schedule_slot(
    slot: dict,
    room: str,
    proposal_titles: list[str],
) -> ScheduleSlot:
    now = utcnow()

    return ScheduleSlot(
        room=room,
        slot_date=slot["slot_date"],
        day_name=slot["day_name"],
        day_label=slot["day_label"],
        time_label=slot["time_label"],
        display_label=slot["display_label"],
        start_at=slot["start_at"],
        end_at=slot["end_at"],
        proposal_titles=proposal_titles,
        proposal_count=len(proposal_titles),
        is_past=is_in_past(slot["start_at"], now),
        is_locked=is_vote_locked(slot["start_at"], now),
    )
