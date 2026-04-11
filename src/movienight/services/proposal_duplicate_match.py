def is_duplicate_proposal(
    proposal,
    room: str,
    normalized_title: str,
) -> bool:
    same_room = proposal.room == room
    same_movie = proposal.movie_title.strip().lower() == normalized_title
    return same_room and same_movie
