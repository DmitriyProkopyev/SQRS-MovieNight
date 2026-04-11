def clean_default_user_credentials(
    username,
    password,
) -> tuple[str, str]:
    return username.strip(), password.strip()
