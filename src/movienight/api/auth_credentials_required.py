from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials


def require_credentials(
    credentials: HTTPAuthorizationCredentials | None,
) -> HTTPAuthorizationCredentials:
    if credentials is not None:
        return credentials

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Malformed authentication request.",
    )
