from movienight.services.auth_password_error import raise_invalid_password
from movienight.services.auth_password_matchers import (
    has_digit,
    has_lowercase,
    has_special,
    has_uppercase,
)


def ensure_password_complexity(password: str) -> None:
    if all(
        (
            has_uppercase(password),
            has_lowercase(password),
            has_digit(password),
            has_special(password),
        )
    ):
        return

    raise_invalid_password()
