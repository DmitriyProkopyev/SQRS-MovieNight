from proxy.services.voting_component_step import (
    process_component_item,
)
from proxy.services.voting_seen_guard import (
    should_skip_component_item,
)


def collect_conflict_component(
    target,
    room_proposals,
):
    component = []
    stack = [target]
    seen_ids: set[int] = set()

    while stack:
        current = stack.pop()
        if should_skip_component_item(current.id, seen_ids):
            continue

        process_component_item(
            current=current,
            room_proposals=room_proposals,
            component=component,
            stack=stack,
            seen_ids=seen_ids,
        )

    return component
