from fastapi import HTTPException, status


def normalize_username(username: str) -> str:
    value = username.strip()
    if value:
        return value

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Username cannot be empty.",
    )
