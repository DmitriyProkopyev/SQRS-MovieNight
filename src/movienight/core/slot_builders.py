from datetime import UTC, date, datetime, time, timedelta

from movienight.core.slot_constants import SLOT_DURATION_HOURS
from movienight.core.slot_labels import (
    build_display_label,
    build_time_label,
)


def build_slot_start(
    slot_date: date,
    hour: int,
) -> datetime:
    return datetime.combine(
        slot_date,
        time(hour=hour, minute=0, tzinfo=UTC),
    )


def build_slot(
    slot_date: date,
    hour: int,
) -> dict:
    start_at = build_slot_start(slot_date, hour)
    end_at = start_at + timedelta(hours=SLOT_DURATION_HOURS)

    day_label = slot_date.strftime("%a %d.%m")
    time_label = build_time_label(start_at, end_at)

    return {
        "slot_date": slot_date,
        "day_name": slot_date.strftime("%A"),
        "day_label": day_label,
        "time_label": time_label,
        "start_at": start_at,
        "end_at": end_at,
        "display_label": build_display_label(day_label, time_label),
    }
