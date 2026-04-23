from proxy.services.reaction_past_guard import (
    ensure_not_past_for_reaction_add,
)
from proxy.services.reaction_presence_guard import (
    ensure_reaction_category_not_exists,
)
from proxy.services.reaction_target_guard import (
    ensure_valid_reaction_add_target,
)


def ensure_reaction_add_allowed(
    has_same_category: bool,
    is_target: bool,
    proposal,
    now,
) -> None:
    ensure_not_past_for_reaction_add(
        proposal=proposal,
        now=now,
    )
    ensure_valid_reaction_add_target(is_target)
    ensure_reaction_category_not_exists(has_same_category)
