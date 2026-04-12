import unicodedata

from fastapi import HTTPException, status


def ensure_printable_movie_title(title: str) -> None:
    for char in title:
        if unicodedata.category(char).startswith("C"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Movie title cannot contain "
                    "esoteric non-printable characters."
                ),
            )
