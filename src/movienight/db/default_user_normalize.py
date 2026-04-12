from movienight.db.default_user_clean import (
    clean_default_user_credentials,
)
from movienight.db.default_user_nonempty import (
    has_nonempty_default_user_credentials,
)
from movienight.db.default_user_presence import (
    has_default_user_credentials,
)


def normalize_default_user_credentials(
    username,
    password,
) -> tuple[str, str] | None:
    if not has_default_user_credentials(username, password):
        return None

    normalized_username, normalized_password = (
        clean_default_user_credentials(username, password)
    )
    if not has_nonempty_default_user_credentials(
        normalized_username,
        normalized_password,
    ):
        return None

    return normalized_username, normalized_password
