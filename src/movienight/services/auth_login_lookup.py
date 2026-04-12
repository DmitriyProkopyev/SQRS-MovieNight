from movienight.core.password_hasher import verify_password
from movienight.services.auth_invalid_credentials import (
    raise_invalid_credentials,
)


def require_login_user(
    users_repo,
    username: str,
    password: str,
):
    user = users_repo.get_by_username(username.strip())
    if user is None:
        raise_invalid_credentials()

    if not verify_password(password, user.password_hash):
        raise_invalid_credentials()

    return user
