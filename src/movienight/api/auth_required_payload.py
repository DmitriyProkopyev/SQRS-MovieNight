from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials

from movienight.api.auth_scheme import bearer_scheme
from movienight.api.auth_user_resolver import resolve_auth_payload


def resolve_required_auth_payload(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
) -> dict:
    if not request.headers.get("authorization"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    return resolve_auth_payload(credentials)
