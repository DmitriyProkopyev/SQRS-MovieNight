from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from movienight.api.auth_user_resolver import resolve_auth_payload
from movienight.db.session import get_db
from movienight.repositories.revoked_tokens import RevokedTokenRepository
from movienight.repositories.users import UserRepository


def _load_current_user(
    db: Session,
    payload: dict,
):
    user_id = int(payload["sub"])
    jti = payload["jti"]

    if RevokedTokenRepository(db).exists(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is no longer valid.",
        )

    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    return user


def get_current_user(
    db: Session = Depends(get_db),
    payload: dict = Depends(resolve_auth_payload),
):
    return _load_current_user(db, payload)


def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    authorization = request.headers.get("authorization")
    if not authorization:
        return None

    parts = authorization.split(" ", 1)
    if len(parts) != 2:
        return None

    scheme, token = parts
    credentials = HTTPAuthorizationCredentials(
        scheme=scheme,
        credentials=token,
    )

    try:
        payload = resolve_auth_payload(credentials)
        return _load_current_user(db, payload)
    except HTTPException:
        return None