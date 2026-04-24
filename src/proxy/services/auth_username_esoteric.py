import unicodedata

from fastapi import HTTPException, status


def ensure_no_esoteric_characters(username: str) -> None:
    for char in username:
        category = unicodedata.category(char)
        if category.startswith("C"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Username cannot contain "
                    "esoteric or invisible characters."
                ),
            )
