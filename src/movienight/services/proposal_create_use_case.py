from movienight.core.clock import utcnow
from movienight.db.models import Proposal
from movienight.services.proposal_conflict_validation import (
    ensure_creation_allowed,
)
from movienight.services.proposal_response_builder import (
    build_created_proposal_response,
)
from movienight.services.proposal_room_validation import (
    ensure_existing_room,
)
from movienight.services.proposal_time_validation import (
    validate_proposal_time_bounds,
)
from movienight.services.proposal_title_charset import (
    ensure_printable_movie_title,
)
from movienight.services.proposal_title_length import (
    ensure_movie_title_length,
)
from movienight.services.proposal_title_normalization import (
    normalize_movie_title,
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

    movie_title = normalize_movie_title(payload.movie_title)
    ensure_printable_movie_title(movie_title)
    ensure_movie_title_length(movie_title)

    room = ensure_existing_room(payload.room)
    room_proposals = proposals_repo.list_by_room(room)

    ensure_creation_allowed(
        room=room,
        movie_title=movie_title,
        starts_at=starts_at,
        ends_at=ends_at,
        existing_room_proposals=room_proposals,
        now=now,
    )

    proposal = proposals_repo.create(
        Proposal(
            creator_id=current_user.id,
            room=room,
            movie_title=movie_title,
            starts_at=starts_at,
            ends_at=ends_at,
            created_at=now,
        )
    )
    return build_created_proposal_response(proposal)
