def map_vote_count_rows(rows) -> dict[int, int]:
    return {
        proposal_id: int(count)
        for proposal_id, count in rows
    }
