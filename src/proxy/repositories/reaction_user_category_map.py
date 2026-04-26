def map_user_category_rows(rows) -> dict[int, list[str]]:
    result: dict[int, list[str]] = {}

    for proposal_id, category in rows:
        result.setdefault(proposal_id, []).append(category.value)

    return result
