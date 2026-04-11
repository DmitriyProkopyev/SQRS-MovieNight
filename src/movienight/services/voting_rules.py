from datetime import datetime

from fastapi import HTTPException, status

from movienight.core.clock import as_utc
from movienight.db.models import Proposal
from movienight.services.schedule_rules import (
    overlaps,
    is_in_past,
    is_vote_locked
)


def build_conflict_component(
    target: Proposal,
    room_proposals: list[Proposal]
) -> list[Proposal]:
    component: list[Proposal] = []
    stack = [target]
    seen_ids: set[int] = set()

    while stack:
        current = stack.pop()
        if current.id in seen_ids:
            continue

        seen_ids.add(current.id)
        component.append(current)

        neighbors = [
            proposal
            for proposal in room_proposals
            if proposal.id != current.id and
            overlaps(
                current.starts_at,
                current.ends_at,
                proposal.starts_at,
                proposal.ends_at,
            )
        ]
        stack.extend(neighbors)

    component.sort(
        key=lambda item: (
            as_utc(item.starts_at),
            as_utc(item.created_at),
            item.id,
        )
    )
    return component


def choose_winner(
    component: list[Proposal],
    vote_counts: dict[int, int]
) -> Proposal:
    ranked = sorted(
        component,
        key=lambda item: (
            -vote_counts.get(item.id, 0),
            as_utc(item.created_at),
            item.id,
        ),
    )
    return ranked[0]


def is_reaction_target(
    proposal: Proposal,
    component: list[Proposal],
    vote_counts: dict[int, int],
    now: datetime,
) -> bool:
    starts_at = as_utc(proposal.starts_at)
    now = as_utc(now)

    if is_in_past(starts_at, now):
        return False

    if not is_vote_locked(starts_at, now):
        return False

    if len(component) == 1:
        return True

    winner = choose_winner(component, vote_counts)
    return proposal.id == winner.id


def ensure_vote_allowed(
    proposal: Proposal,
    current_user_id: int,
    user_votes_in_group: list[int],
    already_voted_for_target: bool,
    now: datetime,
) -> None:
    starts_at = as_utc(proposal.starts_at)
    now = as_utc(now)

    if proposal.creator_id == current_user_id:
        _raise_bad_request(
            "You cannot vote for "
            "your own proposal."
        )
    if is_in_past(starts_at, now) or is_vote_locked(starts_at, now):
        _raise_bad_request(
            "Voting is not allowed for "
            "this proposal anymore."
        )
    if already_voted_for_target:
        _raise_bad_request(
            "You have already voted "
            "for this proposal."
        )
    if user_votes_in_group:
        _raise_bad_request(
            "You have already voted "
            "in this voting group."
        )


def ensure_vote_removal_allowed(
    has_vote: bool,
    proposal: Proposal,
    now: datetime
) -> None:
    starts_at = as_utc(proposal.starts_at)
    now = as_utc(now)

    if not has_vote:
        _raise_bad_request(
            "You have not voted "
            "for this proposal."
        )
    if is_in_past(starts_at, now) or is_vote_locked(starts_at, now):
        _raise_bad_request(
            "Vote cancellation is not "
            "allowed for this proposal anymore."
        )


def ensure_reaction_add_allowed(
    has_same_category: bool,
    is_target: bool,
    proposal: Proposal,
    now: datetime,
) -> None:
    starts_at = as_utc(proposal.starts_at)
    now = as_utc(now)

    if is_in_past(starts_at, now):
        _raise_bad_request(
            "Food reactions cannot be added to past proposals."
        )
    if not is_target:
        _raise_bad_request(
            "Food reactions are allowed only for the "
            "selected winner during the final hour before start."
        )
    if has_same_category:
        _raise_bad_request(
            "You have already added this food reaction category."
        )


def ensure_reaction_delete_allowed(
    has_reaction: bool,
    is_target: bool,
    proposal: Proposal,
    now: datetime,
) -> None:
    starts_at = as_utc(proposal.starts_at)
    now = as_utc(now)

    if is_in_past(starts_at, now):
        _raise_bad_request(
            "Food reactions cannot be removed from past proposals."
        )
    if not is_target:
        _raise_bad_request(
            "Food reactions can be removed only for the "
            "selected winner during the final hour before start."
        )
    if not has_reaction:
        _raise_bad_request(
            "You have not added this food reaction category to the proposal."
        )


def _raise_bad_request(message: str) -> None:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=message
    )
