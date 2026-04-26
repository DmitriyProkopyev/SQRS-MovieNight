def build_reaction_permissions(
    reaction_block_active: bool,
    my_reactions: list[str],
) -> dict[str, bool]:
    return {
        "can_add_reaction": reaction_block_active,
        "can_remove_reaction": (
            reaction_block_active and bool(my_reactions)
        ),
    }
