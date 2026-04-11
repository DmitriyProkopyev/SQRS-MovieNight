from datetime import datetime

from movienight.services.home_card_response_builder import (
    build_proposal_card,
)
from movienight.services.home_card_state_context import (
    build_card_state_context,
)
from movienight.services.home_card_times import normalize_card_times
from movienight.services.home_winner_flag import is_winner_flag


def map_card(
    proposal,
    component,
    component_vote_counts: dict[int, int],
    votes_count: int,
    my_vote: bool,
    reactions: dict[str, int],
    my_reactions: list[str],
    current_user,
    now: datetime,
    winner_id: int | None,
):
    starts_at, ends_at, created_at, normalized_now = normalize_card_times(
        proposal=proposal,
        now=now,
    )
    state = build_card_state_context(
        proposal=proposal,
        component=component,
        component_vote_counts=component_vote_counts,
        my_vote=my_vote,
        reactions=reactions,
        my_reactions=my_reactions,
        current_user=current_user,
        now=normalized_now,
    )

    return build_proposal_card(
        proposal=proposal,
        starts_at=starts_at,
        ends_at=ends_at,
        created_at=created_at,
        votes_count=votes_count,
        my_vote=my_vote,
        is_past=state["is_past"],
        is_winner=is_winner_flag(proposal.id, winner_id),
        vote_state=state["vote_state"],
        reaction_state=state["reaction_state"],
    )
