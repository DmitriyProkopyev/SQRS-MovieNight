from proxy.services.auth_username_esoteric import (
    ensure_no_esoteric_characters,
)
from proxy.services.auth_username_punctuation import (
    ensure_no_forbidden_punctuation,
)


def ensure_valid_username_charset(username: str) -> None:
    ensure_no_esoteric_characters(username)
    ensure_no_forbidden_punctuation(username)
