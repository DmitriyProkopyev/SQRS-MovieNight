from datetime import date, datetime, timedelta

from movienight.core.clock import as_utc, utcnow


def get_current_week_bounds(
    now: datetime | None = None,
) -> tuple[date, date]:
    reference = as_utc(now or utcnow())
    week_start = (
        reference - timedelta(days=reference.weekday())
    ).date()
    week_end = week_start + timedelta(days=6)
    return week_start, week_end
