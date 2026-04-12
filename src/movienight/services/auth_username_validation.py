from movienight.services.auth_username_charset import (
    ensure_valid_username_charset,
)
from movienight.services.auth_username_length import (
    ensure_username_length,
)


def normalize_username(username: str) -> str:
    return username.strip()


def ensure_valid_username(username: str) -> None:
    ensure_username_length(username)
    ensure_valid_username_charset(username)
