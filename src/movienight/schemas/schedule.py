from datetime import date, datetime

from pydantic import BaseModel


class ScheduleSlot(BaseModel):
    room: str
    day_name: str
    day_label: str
    slot_date: date
    time_label: str
    start_at: datetime
    end_at: datetime
    display_label: str
    proposal_titles: list[str]
    proposal_count: int
    is_past: bool
    is_locked: bool


class RoomSchedule(BaseModel):
    room: str
    slots: list[ScheduleSlot]


class ScheduleResponse(BaseModel):
    week_start: date
    week_end: date
    rooms: list[RoomSchedule]
