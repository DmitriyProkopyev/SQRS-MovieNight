from movienight.db.default_user_normalize import (
    normalize_default_user_credentials,
)
from movienight.db.default_user_raw import (
    get_raw_default_user_credentials,
)


def get_default_user_credentials() -> tuple[str, str] | None:
    username, password = get_raw_default_user_credentials()
    return normalize_default_user_credentials(username, password)
