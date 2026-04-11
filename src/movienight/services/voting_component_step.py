from movienight.services.voting_neighbors import find_neighbors


def process_component_item(
    current,
    room_proposals,
    component,
    stack,
    seen_ids: set[int],
) -> None:
    seen_ids.add(current.id)
    component.append(current)
    stack.extend(find_neighbors(current, room_proposals))
