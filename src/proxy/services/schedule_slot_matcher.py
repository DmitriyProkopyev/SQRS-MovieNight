from datetime import datetime

from proxy.db.models import Proposal
from proxy.services.time_overlap import overlaps


def find_matching_proposals(
    proposals: list[Proposal],
    start_at: datetime,
    end_at: datetime,
) -> list[Proposal]:
    return [
        proposal
        for proposal in proposals
        if overlaps(
            start_at,
            end_at,
            proposal.starts_at,
            proposal.ends_at,
        )
    ]
