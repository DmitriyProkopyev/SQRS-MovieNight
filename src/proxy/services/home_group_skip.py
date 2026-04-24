def should_skip_group_proposal(
    proposal_id: int,
    visited: set[int],
) -> bool:
    return proposal_id in visited
