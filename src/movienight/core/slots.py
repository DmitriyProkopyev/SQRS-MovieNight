from datetime import UTC, date, datetime, time, timedelta

from movienight.core.clock import as_utc, utcnow

SLOT_DURATION_HOURS = 2
ROOMS: tuple[str, ...] = ("Room A", "Room B", "Room C", "Room D")


def get_current_week_bounds(now: datetime | None = None) -> tuple[date, date]:
    reference = as_utc(now or utcnow())
    week_start = (reference - timedelta(days=reference.weekday())).date()
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def iter_week_slots(week_start: date) -> list[dict]:
    slots: list[dict] = []

    for day_offset in range(7):
        slot_date = week_start + timedelta(days=day_offset)

        for hour in range(0, 24, SLOT_DURATION_HOURS):
            start_at = datetime.combine(
                slot_date,
                time(hour=hour, minute=0, tzinfo=UTC),
            )
            end_at = start_at + timedelta(hours=SLOT_DURATION_HOURS)

            slots.append(
                {
                    "slot_date": slot_date,
                    "day_name": slot_date.strftime("%A"),
                    "day_label": slot_date.strftime("%a %d.%m"),
                    "time_label": (
                        f"{start_at.strftime('%H:%M')}–"
                        f"{end_at.strftime('%H:%M')}"
                    ),
                    "start_at": start_at,
                    "end_at": end_at,
                    "display_label": (
                        f"{slot_date.strftime('%A %d.%m')} | "
                        f"{start_at.strftime('%H:%M')}–"
                        f"{end_at.strftime('%H:%M')}"
                    ),
                }
            )

    return slots


def is_fixed_two_hour_slot(starts_at: datetime, ends_at: datetime) -> bool:
    starts_at = as_utc(starts_at)
    ends_at = as_utc(ends_at)

    if (
        starts_at.minute != 0 or
        starts_at.second != 0 or
        starts_at.microsecond != 0
    ):
        return False

    if starts_at.hour % SLOT_DURATION_HOURS != 0:
        return False

    return (
        ends_at - starts_at ==
        timedelta(hours=SLOT_DURATION_HOURS)
    )
