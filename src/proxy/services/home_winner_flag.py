def is_winner_flag(
    proposal_id: int,
    winner_id: int | None,
) -> bool:
    return winner_id is not None and winner_id == proposal_id
