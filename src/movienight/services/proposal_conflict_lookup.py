from datetime import datetime

from movienight.db.models import Proposal
from movienight.services.time_overlap import overlaps


def find_conflicts(
    target_room: str,
    starts_at: datetime,
    ends_at: datetime,
    proposals: list[Proposal],
) -> list[Proposal]:
    return [
        proposal
        for proposal in proposals
        if proposal.room == target_room and
        overlaps(
            starts_at,
            ends_at,
            proposal.starts_at,
            proposal.ends_at,
        )
    ]
