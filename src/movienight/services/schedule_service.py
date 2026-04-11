from sqlalchemy.orm import Session

from movienight.core.clock import as_utc, utcnow
from movienight.core.slots import (
    ROOMS,
    get_current_week_bounds,
    iter_week_slots
)
from movienight.repositories.proposals import ProposalRepository
from movienight.schemas.schedule import (
    RoomSchedule,
    ScheduleResponse,
    ScheduleSlot
)
from movienight.services.schedule_rules import (
    is_vote_locked,
    overlaps
)


class ScheduleService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.proposals = ProposalRepository(db)

    def get_week_schedule(self) -> ScheduleResponse:
        now = utcnow()
        week_start, week_end = get_current_week_bounds(now)
        proposals = self.proposals.list_all()

        room_schedules: list[RoomSchedule] = []

        for room in ROOMS:
            room_slots: list[ScheduleSlot] = []

            for slot in iter_week_slots(week_start):
                start_at = slot["start_at"]
                end_at = slot["end_at"]

                matching = [
                    proposal
                    for proposal in proposals
                    if proposal.room == room and
                    overlaps(
                        start_at,
                        end_at,
                        proposal.starts_at,
                        proposal.ends_at
                    )
                ]

                room_slots.append(
                    ScheduleSlot(
                        room=room,
                        day_name=slot["day_name"],
                        day_label=slot["day_label"],
                        slot_date=slot["slot_date"],
                        time_label=slot["time_label"],
                        start_at=start_at,
                        end_at=end_at,
                        display_label=slot["display_label"],
                        proposal_titles=[
                            proposal.movie_title for proposal in matching
                        ],
                        proposal_count=len(matching),
                        is_past=as_utc(start_at) < as_utc(now),
                        is_locked=is_vote_locked(start_at, now),
                    )
                )

            room_schedules.append(
                RoomSchedule(
                    room=room,
                    slots=room_slots
                )
            )

        return ScheduleResponse(
            week_start=week_start,
            week_end=week_end,
            rooms=room_schedules,
        )
