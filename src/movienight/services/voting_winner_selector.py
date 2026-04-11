from movienight.db.models import Proposal


def choose_winner(
    component: list[Proposal],
    vote_counts: dict[int, int],
) -> Proposal:
    ranked = sorted(
        component,
        key=lambda item: (
            -vote_counts.get(item.id, 0),
            item.created_at,
            item.id,
        ),
    )
    return ranked[0]
