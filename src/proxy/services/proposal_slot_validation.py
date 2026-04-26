from datetime import datetime

from proxy.services.proposal_duration_validation import (
    ensure_two_hour_duration,
)
from proxy.services.proposal_slot_start_validation import (
    ensure_valid_slot_start,
)


def validate_fixed_two_hour_slot(
    starts_at: datetime,
    ends_at: datetime,
) -> None:
    ensure_two_hour_duration(
        starts_at=starts_at,
        ends_at=ends_at,
    )
    ensure_valid_slot_start(starts_at)
