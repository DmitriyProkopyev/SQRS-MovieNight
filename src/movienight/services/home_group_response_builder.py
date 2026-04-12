from movienight.schemas.home import ProposalGroup
from movienight.services.schedule_rules import is_vote_locked


def build_proposal_group(
    component,
    starts_at,
    ends_at,
    winner_id: int | None,
    cards,
    now,
) -> ProposalGroup:
    return ProposalGroup(
        room=component[0].room,
        starts_at=starts_at,
        ends_at=ends_at,
        is_conflict=len(component) > 1,
        is_locked=is_vote_locked(starts_at, now),
        winner_proposal_id=winner_id,
        proposals=cards,
    )
