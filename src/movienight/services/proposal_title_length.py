from fastapi import HTTPException, status

MAX_MOVIE_TITLE_LENGTH = 255


def ensure_movie_title_length(title: str) -> None:
    if len(title) <= MAX_MOVIE_TITLE_LENGTH:
        return

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Movie title length cannot exceed 255 characters.",
    )
