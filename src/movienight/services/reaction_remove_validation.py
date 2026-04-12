from movienight.services.reaction_past_guard import (
    ensure_not_past_for_reaction_remove,
)
from movienight.services.reaction_presence_guard import (
    ensure_reaction_exists,
)
from movienight.services.reaction_target_guard import (
    ensure_valid_reaction_remove_target,
)


def ensure_reaction_delete_allowed(
    has_reaction: bool,
    is_target: bool,
    proposal,
    now,
) -> None:
    ensure_not_past_for_reaction_remove(
        proposal=proposal,
        now=now,
    )
    ensure_valid_reaction_remove_target(is_target)
    ensure_reaction_exists(has_reaction)
