import string

from fastapi import HTTPException, status

ALLOWED_PUNCTUATION = {"_", "-"}


def ensure_no_forbidden_punctuation(username: str) -> None:
    for char in username:
        if char in string.punctuation and char not in ALLOWED_PUNCTUATION:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Punctuation characters are "
                    "not allowed in the username."
                ),
            )
