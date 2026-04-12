def should_skip_component_item(
    item_id: int,
    seen_ids: set[int],
) -> bool:
    return item_id in seen_ids
