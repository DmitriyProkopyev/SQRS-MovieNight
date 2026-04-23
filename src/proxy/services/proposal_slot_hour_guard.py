from proxy.services.schedule_exceptions import raise_bad_request


def ensure_even_slot_hour(starts_at) -> None:
    if starts_at.hour % 2 == 0:
        return

    raise_bad_request(
        "Proposal start time must match a 2-hour slot: "
        "00:00, 02:00, 04:00, and so on."
    )
