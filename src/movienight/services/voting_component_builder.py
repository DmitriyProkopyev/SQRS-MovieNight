from movienight.services.voting_component_collect import (
    collect_conflict_component,
)
from movienight.services.voting_sort_key import component_sort_key


def build_conflict_component(
    target,
    room_proposals,
):
    component = collect_conflict_component(
        target=target,
        room_proposals=room_proposals,
    )
    component.sort(key=component_sort_key)
    return component
