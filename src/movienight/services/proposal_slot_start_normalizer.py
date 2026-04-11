from movienight.core.clock import as_utc


def normalize_slot_start(starts_at):
    return as_utc(starts_at)
