from proxy.db.models import Proposal


def build_component_vote_counts(
    component: list[Proposal],
    vote_counts: dict[int, int],
) -> dict[int, int]:
    return {
        item.id: vote_counts.get(item.id, 0)
        for item in component
    }
