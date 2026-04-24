def is_slot_start_valid(starts_at) -> bool:
    return (
        starts_at.minute == 0 and
        starts_at.second == 0 and
        starts_at.microsecond == 0 and
        starts_at.hour % 2 == 0
    )
