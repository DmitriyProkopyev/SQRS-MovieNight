from sqlalchemy.orm import Session

from proxy.repositories.reaction_user_category_map import (
    map_user_category_rows,
)
from proxy.repositories.reaction_user_category_rows import (
    load_user_category_rows,
)


def user_categories_for_proposal_ids(
    db: Session,
    user_id: int,
    proposal_ids: list[int],
) -> dict[int, list[str]]:
    rows = load_user_category_rows(db, user_id, proposal_ids)
    return map_user_category_rows(rows)
