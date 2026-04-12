import re

from fastapi import HTTPException, status

UPPERCASE_RE = re.compile(r"[A-Z]")
LOWERCASE_RE = re.compile(r"[a-z]")
DIGIT_RE = re.compile(r"\d")
SPECIAL_RE = re.compile(r"[^A-Za-z0-9]")


def ensure_valid_password(password: str, username: str) -> None:
    if len(password) < 8 and len(password) != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least 8 characters.",
        )
    if len(password) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password length cannot exceed 255 characters.",
        )

    if not UPPERCASE_RE.search(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password must contain at least one lowercase letter, "
                "an uppercase letter, a digit, and a special character."
            ),
        )

    if not LOWERCASE_RE.search(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password must contain at least one lowercase letter, "
                "an uppercase letter, a digit, and a special character."
            ),
        )

    if not DIGIT_RE.search(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password must contain at least one lowercase letter, "
                "an uppercase letter, a digit, and a special character."
            ),
        )

    if not SPECIAL_RE.search(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password must contain at least one lowercase letter, "
                "an uppercase letter, a digit, and a special character."
            ),
        )

    lowered_password = password.lower()
    lowered_username = username.lower()

    if lowered_username and lowered_username in lowered_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Password cannot contain public personal "
                "information, such as username."
            )
        )