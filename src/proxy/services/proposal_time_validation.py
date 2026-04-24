from datetime import datetime

from proxy.services.proposal_basic_time_validation import (
    validate_basic_time_bounds,
)
from proxy.services.proposal_slot_validation import (
    validate_fixed_two_hour_slot,
)


def validate_proposal_time_bounds(
    starts_at: datetime,
    ends_at: datetime,
    now: datetime,
) -> None:
    validate_basic_time_bounds(
        starts_at=starts_at,
        ends_at=ends_at,
        now=now,
    )
    validate_fixed_two_hour_slot(
        starts_at=starts_at,
        ends_at=ends_at,
    )
