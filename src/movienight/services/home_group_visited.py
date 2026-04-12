def mark_component_visited(
    visited: set[int],
    component,
) -> None:
    visited.update(item.id for item in component)
