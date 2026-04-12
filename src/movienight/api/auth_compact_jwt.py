from fastapi import HTTPException, status


def require_compact_jwt(token: str) -> None:
    if token.count(".") == 2:
        return

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Malformed authentication request.",
    )
