from datetime import datetime

from proxy.db.models import Proposal
from proxy.services.voting_rules import is_reaction_target


def is_reaction_block_active(
    proposal: Proposal,
    component: list[Proposal],
    component_vote_counts: dict[int, int],
    now: datetime,
) -> bool:
    return is_reaction_target(
        proposal=proposal,
        component=component,
        vote_counts=component_vote_counts,
        now=now,
    )
