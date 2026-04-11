from datetime import datetime

from movienight.core.clock import as_utc


def is_in_past(point: datetime, now: datetime) -> bool:
    return as_utc(point) < as_utc(now)
