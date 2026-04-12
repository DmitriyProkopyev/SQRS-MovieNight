from datetime import datetime

from movienight.core.clock import as_utc
from movienight.services.schedule_exceptions import raise_bad_request
from movienight.services.time_past_check import is_in_past


def validate_basic_time_bounds(
    starts_at: datetime,
    ends_at: datetime,
    now: datetime,
) -> None:
    starts_at = as_utc(starts_at)
    ends_at = as_utc(ends_at)
    now = as_utc(now)

    if is_in_past(starts_at, now):
        raise_bad_request("Proposal start time cannot be in the past.")

    if ends_at <= starts_at:
        raise_bad_request(
            "Proposal end time must be later than start time."
        )
