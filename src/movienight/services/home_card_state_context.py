from datetime import datetime

from movienight.services.home_reaction_state import (
    build_reaction_state,
)
from movienight.services.home_vote_state import build_vote_state
from movienight.services.schedule_rules import is_in_past, is_vote_locked


def build_card_state_context(
    proposal,
    component,
    component_vote_counts: dict[int, int],
    my_vote: bool,
    reactions: dict[str, int],
    my_reactions: list[str],
    current_user,
    now: datetime,
) -> dict:
    is_past_value = is_in_past(proposal.starts_at, now)
    vote_locked = is_vote_locked(proposal.starts_at, now)

    vote_state = build_vote_state(
        proposal=proposal,
        current_user=current_user,
        my_vote=my_vote,
        vote_locked=vote_locked,
        is_past=is_past_value,
    )
    reaction_state = build_reaction_state(
        proposal=proposal,
        component=component,
        component_vote_counts=component_vote_counts,
        reactions=reactions,
        my_reactions=my_reactions,
        now=now,
    )

    return {
        "is_past": is_past_value,
        "vote_state": vote_state,
        "reaction_state": reaction_state,
    }
