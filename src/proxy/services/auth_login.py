from proxy.services.auth_login_guard import (
    ensure_not_authenticated_for_login,
)
from proxy.services.auth_login_lookup import require_login_user
from proxy.services.auth_token_builder import build_login_response


def login_user(
    payload,
    current_user,
    users_repo,
):
    ensure_not_authenticated_for_login(current_user)

    user = require_login_user(
        users_repo=users_repo,
        username=payload.username,
        password=payload.password,
    )
    return build_login_response(user)
