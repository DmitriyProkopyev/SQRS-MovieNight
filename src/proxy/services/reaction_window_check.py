from proxy.services.time_past_check import is_in_past
from proxy.services.time_vote_lock import is_vote_locked


def is_reaction_window_open(
    proposal,
    now,
) -> bool:
    if is_in_past(proposal.starts_at, now):
        return False

    return is_vote_locked(proposal.starts_at, now)
