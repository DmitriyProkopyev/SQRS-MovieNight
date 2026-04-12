def sort_home_groups(groups):
    return sorted(
        groups,
        key=lambda group: (
            group.starts_at,
            group.room,
        ),
    )
