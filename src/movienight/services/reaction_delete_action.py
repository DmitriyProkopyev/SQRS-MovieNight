def delete_reaction_and_count(
    reactions_repo,
    reaction,
    proposal_id: int,
    category: str,
) -> int:
    reactions_repo.delete(reaction)
    return reactions_repo.count_for_proposal_and_category(
        proposal_id,
        category,
    )
