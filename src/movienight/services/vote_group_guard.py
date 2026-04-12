from movienight.services.schedule_exceptions import raise_bad_request


def ensure_no_group_vote(
    user_votes_in_group: list[int],
) -> None:
    if not user_votes_in_group:
        return

    raise_bad_request(
        "You have already voted in this voting group."
    )
