from datetime import datetime

from movienight.core.clock import as_utc


def overlaps(
    start_a: datetime,
    end_a: datetime,
    start_b: datetime,
    end_b: datetime,
) -> bool:
    start_a = as_utc(start_a)
    end_a = as_utc(end_a)
    start_b = as_utc(start_b)
    end_b = as_utc(end_b)
    return start_a < end_b and start_b < end_a
