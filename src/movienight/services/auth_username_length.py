from fastapi import HTTPException, status


def ensure_username_length(username: str) -> None:
    if len(username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username should contain at least three characters.",
        )

    if len(username) >= 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username length cannot exceed 100 characters.",
        )