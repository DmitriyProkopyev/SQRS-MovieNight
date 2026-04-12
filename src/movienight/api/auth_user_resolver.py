from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from movienight.api.auth_scheme import bearer_scheme
from movienight.api.auth_token_reader import read_bearer_token
from movienight.core.security import decode_access_token


def resolve_auth_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
) -> dict:
    token = read_bearer_token(credentials)
    payload = decode_access_token(token)

    subject = payload.get("sub")
    jti = payload.get("jti")
    exp = payload.get("exp")
    iat = payload.get("iat")

    if not isinstance(subject, str) or not subject.isdecimal():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed authentication request.",
        )

    if not isinstance(jti, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed authentication request.",
        )

    if not isinstance(exp, int) or not isinstance(iat, int):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed authentication request.",
        )

    return payload