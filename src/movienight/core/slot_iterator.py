from datetime import date, timedelta

from movienight.core.slot_builders import build_slot
from movienight.core.slot_constants import SLOT_DURATION_HOURS


def iter_week_slots(week_start: date) -> list[dict]:
    slots: list[dict] = []

    for day_offset in range(7):
        slot_date = week_start + timedelta(days=day_offset)
        slots.extend(iter_day_slots(slot_date))

    return slots


def iter_day_slots(slot_date: date) -> list[dict]:
    return [
        build_slot(slot_date, hour)
        for hour in range(0, 24, SLOT_DURATION_HOURS)
    ]
