def is_valid_slot_start(starts_at) -> bool:
    return (
        starts_at.minute == 0 and
        starts_at.second == 0 and
        starts_at.microsecond == 0 and
        starts_at.hour % 2 == 0
    )
