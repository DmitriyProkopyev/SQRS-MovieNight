from sqlalchemy.orm import Session

from movienight.core.slots import (
    ROOMS,
    get_current_week_bounds,
    iter_week_slots,
)
from movienight.repositories.proposals import ProposalRepository
from movienight.schemas.schedule import ScheduleResponse
from movienight.services.schedule_room_builder import (
    build_room_schedule,
)


class ScheduleService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.proposals = ProposalRepository(db)

    def get_week_schedule(self) -> ScheduleResponse:
        proposals = self.proposals.list_all()
        week_start, week_end = get_current_week_bounds()
        week_slots = iter_week_slots(week_start)

        room_schedules = [
            build_room_schedule(
                room=room,
                proposals=proposals,
                week_slots=week_slots,
            )
            for room in ROOMS
        ]

        return ScheduleResponse(
            week_start=week_start,
            week_end=week_end,
            rooms=room_schedules,
        )
