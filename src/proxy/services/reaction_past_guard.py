from proxy.services.schedule_exceptions import raise_bad_request
from proxy.services.time_past_check import is_in_past


def ensure_not_past_for_reaction_add(
    proposal,
    now,
) -> None:
    if is_in_past(proposal.starts_at, now):
        raise_bad_request(
            "Food reactions cannot be added to past proposals."
        )


def ensure_not_past_for_reaction_remove(
    proposal,
    now,
) -> None:
    if is_in_past(proposal.starts_at, now):
        raise_bad_request(
            "Food reactions cannot be removed from past proposals."
        )
