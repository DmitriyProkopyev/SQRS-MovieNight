from datetime import timedelta

from movienight.core.slot_constants import SLOT_DURATION_HOURS


def is_valid_slot_duration(
    starts_at,
    ends_at,
) -> bool:
    return ends_at - starts_at == timedelta(hours=SLOT_DURATION_HOURS)
