from movienight.services.auth_username_charset import (
    ensure_no_esoteric_characters,
    ensure_no_forbidden_punctuation,
)
from movienight.services.auth_username_length import ensure_username_length


def normalize_username(username: str) -> str:
    return username.strip()


def ensure_valid_username(username: str) -> None:
    ensure_username_length(username)
    ensure_no_esoteric_characters(username)
    ensure_no_forbidden_punctuation(username)