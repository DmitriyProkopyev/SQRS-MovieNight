from sqlalchemy.orm import Session

from proxy.repositories.vote_count_group_map import (
    map_vote_count_rows,
)
from proxy.repositories.vote_count_group_rows import (
    load_vote_count_rows,
)
from proxy.repositories.vote_count_single import count_for_proposal


def count_by_proposal_ids(
    db: Session,
    proposal_ids: list[int],
) -> dict[int, int]:
    rows = load_vote_count_rows(db, proposal_ids)
    return map_vote_count_rows(rows)


__all__ = [
    "count_for_proposal",
    "count_by_proposal_ids",
]
