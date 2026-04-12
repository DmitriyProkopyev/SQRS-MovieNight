from movienight.services.schedule_exceptions import raise_bad_request


def require_existing_reaction(existing):
    if existing is not None:
        return existing

    raise_bad_request(
        "You have not added this food reaction category to the proposal."
    )
