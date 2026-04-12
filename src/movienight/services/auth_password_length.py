from fastapi import HTTPException, status


def ensure_password_length(password: str) -> None:
    if 8 <= len(password) <= 255:
        return

    if len(password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least 8 characters.",
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Password length cannot exceed 255 characters.",
    )
