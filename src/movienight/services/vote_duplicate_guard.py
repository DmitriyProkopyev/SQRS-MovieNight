from movienight.services.schedule_exceptions import raise_bad_request


def ensure_not_duplicate_vote(
    already_voted_for_target: bool,
) -> None:
    if not already_voted_for_target:
        return

    raise_bad_request(
        "You have already voted for this proposal."
    )
