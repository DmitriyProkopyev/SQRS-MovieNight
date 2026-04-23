from proxy.services.schedule_exceptions import raise_bad_request


def ensure_valid_reaction_add_target(is_target: bool) -> None:
    if is_target:
        return

    raise_bad_request(
        "Food reactions are allowed only for the selected winner "
        "during the final hour before start."
    )


def ensure_valid_reaction_remove_target(is_target: bool) -> None:
    if is_target:
        return

    raise_bad_request(
        "Food reactions can be removed only for the selected winner "
        "during the final hour before start."
    )
