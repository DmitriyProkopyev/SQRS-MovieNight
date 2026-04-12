from typing import Any


def build_visible_reactions(
    reaction_block_active: bool,
    reactions: dict[str, int],
    my_reactions: list[str],
) -> dict[str, Any]:
    if reaction_block_active:
        return {
            "visible_reactions": reactions,
            "visible_my_reactions": my_reactions,
        }

    return {
        "visible_reactions": None,
        "visible_my_reactions": [],
    }
