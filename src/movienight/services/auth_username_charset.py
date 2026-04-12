import string
import unicodedata

from fastapi import HTTPException, status

ALLOWED_PUNCTUATION = {"_", "-"}


def ensure_no_esoteric_characters(username: str) -> None:
    for char in username:
        category = unicodedata.category(char)
        if category.startswith("C"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username cannot contain esoteric or invisible characters.",
            )


def ensure_no_forbidden_punctuation(username: str) -> None:
    for char in username:
        if char in string.punctuation and char not in ALLOWED_PUNCTUATION:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Punctuation characters are not allowed in the username.",
            )