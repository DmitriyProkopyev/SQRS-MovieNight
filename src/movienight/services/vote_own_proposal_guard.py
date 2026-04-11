from movienight.services.schedule_exceptions import raise_bad_request


def ensure_not_own_proposal(
    proposal,
    current_user_id: int,
) -> None:
    if proposal.creator_id != current_user_id:
        return

    raise_bad_request("You cannot vote for your own proposal.")
