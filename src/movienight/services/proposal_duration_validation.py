from datetime import datetime, timedelta

from movienight.core.clock import as_utc
from movienight.services.schedule_exceptions import raise_bad_request

_SLOT_DURATION = timedelta(hours=2)


def ensure_two_hour_duration(
    starts_at: datetime,
    ends_at: datetime,
) -> None:
    starts_at = as_utc(starts_at)
    ends_at = as_utc(ends_at)

    if ends_at - starts_at != _SLOT_DURATION:
        raise_bad_request("Proposal must last exactly 2 hours.")
