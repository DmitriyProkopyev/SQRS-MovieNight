from fastapi import HTTPException, status


def require_bearer_scheme(scheme: str) -> None:
    if scheme.lower() == "bearer":
        return

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Malformed authentication request.",
    )
