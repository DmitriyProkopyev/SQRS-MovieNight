def has_default_user_credentials(
    username,
    password,
) -> bool:
    return bool(username and password)
