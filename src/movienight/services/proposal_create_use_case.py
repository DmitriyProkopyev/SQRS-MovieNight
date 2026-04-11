from movienight.core.clock import utcnow
from movienight.db.models import Proposal
from movienight.services.proposal_conflict_validation import (
    ensure_creation_allowed,
)
from movienight.services.proposal_response_builder import (
    build_created_proposal_response,
)
from movienight.services.proposal_time_validation import (
    validate_proposal_time_bounds,
)


def create_proposal_use_case(
    proposals_repo,
    payload,
    current_user,
):
    starts_at = payload.starts_at
    ends_at = payload.ends_at
    now = utcnow()

    validate_proposal_time_bounds(
        starts_at=starts_at,
        ends_at=ends_at,
        now=now,
    )

    room_proposals = proposals_repo.list_by_room(payload.room)
    ensure_creation_allowed(
        room=payload.room,
        movie_title=payload.movie_title,
        starts_at=starts_at,
        ends_at=ends_at,
        existing_room_proposals=room_proposals,
        now=now,
    )

    proposal = proposals_repo.create(
        Proposal(
            creator_id=current_user.id,
            room=payload.room,
            movie_title=payload.movie_title,
            starts_at=starts_at,
            ends_at=ends_at,
            created_at=now,
        )
    )
    return build_created_proposal_response(proposal)
