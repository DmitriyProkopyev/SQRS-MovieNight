def split_authorization_header(value: str | None) -> tuple[str, str] | None:
    if not value:
        return None

    parts = value.split(" ", 1)
    if len(parts) != 2:
        return None

    return parts[0], parts[1]
