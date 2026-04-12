from movienight.services.auth_password_complexity import (
    ensure_password_complexity,
)
from movienight.services.auth_password_length import (
    ensure_password_length,
)
from movienight.services.auth_password_personal_info import (
    ensure_password_has_no_personal_info,
)


def ensure_valid_password(password: str, username: str) -> None:
    ensure_password_length(password)
    ensure_password_complexity(password)
    ensure_password_has_no_personal_info(password, username)
