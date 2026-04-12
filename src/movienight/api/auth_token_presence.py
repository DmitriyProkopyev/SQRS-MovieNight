from fastapi import HTTPException, status


def require_token_value(token: str) -> str:
    value = token.strip()
    if value:
        return value

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Malformed authentication request.",
    )
