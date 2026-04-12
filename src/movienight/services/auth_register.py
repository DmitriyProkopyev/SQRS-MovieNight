from movienight.services.auth_password_validation import (
    ensure_valid_password,
)
from movienight.services.auth_register_guard import (
    ensure_registration_allowed,
)
from movienight.services.auth_register_uniqueness import (
    ensure_username_available,
)
from movienight.services.auth_token_builder import build_login_response
from movienight.services.auth_user_factory import (
    build_user_for_registration,
)
from movienight.services.auth_username_validation import (
    ensure_valid_username,
    normalize_username,
)


def register_user(
    payload,
    current_user,
    users_repo,
):
    ensure_registration_allowed(current_user)

    username = normalize_username(payload.username)
    ensure_valid_username(username)
    ensure_valid_password(payload.password, username)
    ensure_username_available(users_repo, username)

    user = users_repo.create(
        build_user_for_registration(
            username=username,
            password=payload.password,
        )
    )
    return build_login_response(user)
