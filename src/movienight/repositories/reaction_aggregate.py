from sqlalchemy.orm import Session

from movienight.repositories.reaction_count_group_map import (
    map_reaction_count_rows,
)
from movienight.repositories.reaction_count_group_rows import (
    load_reaction_count_rows,
)
from movienight.repositories.reaction_count_single import (
    count_for_proposal_and_category,
)


def counts_for_proposal_ids(
    db: Session,
    proposal_ids: list[int],
) -> dict[int, dict[str, int]]:
    rows = load_reaction_count_rows(db, proposal_ids)
    return map_reaction_count_rows(rows)


__all__ = [
    "count_for_proposal_and_category",
    "counts_for_proposal_ids",
]
