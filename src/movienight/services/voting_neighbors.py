from movienight.db.models import Proposal
from movienight.services.time_overlap import overlaps


def find_neighbors(
    current: Proposal,
    room_proposals: list[Proposal],
) -> list[Proposal]:
    return [
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
