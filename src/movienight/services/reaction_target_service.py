from movienight.core.clock import utcnow
from movienight.services.voting_rules import (
    build_conflict_component,
    is_reaction_target,
)


def is_valid_reaction_target(
    proposal,
    proposals_repo,
    votes_repo,
) -> bool:
    component = build_conflict_component(
        proposal,
        proposals_repo.list_by_room(proposal.room),
    )
    vote_counts = votes_repo.count_by_proposal_ids(
        [item.id for item in component]
    )
    return is_reaction_target(
        proposal=proposal,
        component=component,
        vote_counts=vote_counts,
        now=utcnow(),
    )
