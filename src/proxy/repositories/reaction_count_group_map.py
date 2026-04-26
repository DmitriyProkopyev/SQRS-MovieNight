def map_reaction_count_rows(rows) -> dict[int, dict[str, int]]:
    result: dict[int, dict[str, int]] = {}

    for proposal_id, category, count in rows:
        result.setdefault(proposal_id, {})[category.value] = int(count)

    return result
