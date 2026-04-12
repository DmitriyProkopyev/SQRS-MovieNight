from movienight.services.proposal_slot_hour_guard import (
    ensure_even_slot_hour,
)
from movienight.services.proposal_slot_minute_guard import (
    ensure_slot_starts_on_full_hour,
)
from movienight.services.proposal_slot_start_normalizer import (
    normalize_slot_start,
)


def ensure_valid_slot_start(starts_at) -> None:
    normalized = normalize_slot_start(starts_at)
    ensure_slot_starts_on_full_hour(normalized)
    ensure_even_slot_hour(normalized)
