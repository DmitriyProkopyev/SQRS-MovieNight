def has_nonempty_default_user_credentials(
    username: str,
    password: str,
) -> bool:
    return bool(username and password)
