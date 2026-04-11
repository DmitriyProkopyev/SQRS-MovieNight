from movienight.core.slot_duration_validation import (
    is_valid_slot_duration,
)
from movienight.core.slot_start_validation import is_valid_slot_start


def is_fixed_two_hour_slot(
    starts_at,
    ends_at,
) -> bool:
    return (
        is_valid_slot_start(starts_at) and
        is_valid_slot_duration(starts_at, ends_at)
    )


__all__ = [
    "is_valid_slot_start",
    "is_valid_slot_duration",
    "is_fixed_two_hour_slot",
]
