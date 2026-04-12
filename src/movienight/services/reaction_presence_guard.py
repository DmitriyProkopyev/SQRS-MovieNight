from movienight.services.schedule_exceptions import raise_bad_request


def ensure_reaction_category_not_exists(
    has_same_category: bool,
) -> None:
    if not has_same_category:
        return

    raise_bad_request(
        "You have already added this food reaction category."
    )


def ensure_reaction_exists(
    has_reaction: bool,
) -> None:
    if has_reaction:
        return

    raise_bad_request(
        "You have not added this food reaction category to the proposal."
    )
