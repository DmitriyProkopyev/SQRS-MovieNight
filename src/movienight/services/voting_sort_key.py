from movienight.db.models import Proposal


def component_sort_key(item: Proposal):
    return (
        item.starts_at,
        item.created_at,
        item.id,
    )
