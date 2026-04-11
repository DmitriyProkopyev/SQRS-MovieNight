from movienight.services.proposal_duplicate_match import (
    is_duplicate_proposal,
)
from movienight.services.proposal_duplicate_title import (
    normalized_movie_title,
)
from movienight.services.schedule_exceptions import raise_bad_request


def ensure_not_duplicate(
    room: str,
    movie_title: str,
    starts_at,
    ends_at,
    conflicts,
) -> None:
    normalized_title = normalized_movie_title(movie_title)

    for proposal in conflicts:
        if is_duplicate_proposal(
            proposal=proposal,
            room=room,
            normalized_title=normalized_title,
        ):
            raise_bad_request(
                "An overlapping proposal for the same room "
                "and movie already exists."
            )
