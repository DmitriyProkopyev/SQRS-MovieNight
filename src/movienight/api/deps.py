from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from movienight.core.security import decode_access_token
from movienight.db.models import User
from movienight.db.session import get_db
from movienight.repositories.revoked_tokens import RevokedTokenRepository
from movienight.repositories.users import UserRepository

DbSession = Annotated[Session, Depends(get_db)]

bearer_scheme = HTTPBearer(auto_error=False)


def _extract_bearer_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> str | None:
    if credentials is None:
        return None
    if credentials.scheme.lower() != "bearer":
        return None
    return credentials.credentials.strip()


def get_current_user(
    db: DbSession,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Security(bearer_scheme),
    ] = None,
) -> User:
    token = _extract_bearer_token(credentials)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    payload = decode_access_token(token)

    try:
        jti = str(payload.get("jti", ""))
        user_id = int(payload.get("sub", 0))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )

    if not jti or user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )

    revoked_repo = RevokedTokenRepository(db)
    if revoked_repo.exists(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is no longer valid.",
        )

    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    return user


def get_optional_current_user(
    db: DbSession,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Security(bearer_scheme),
    ] = None,
) -> User | None:
    token = _extract_bearer_token(credentials)
    if not token:
        return None

    try:
        payload = decode_access_token(token)
        jti = str(payload.get("jti", ""))
        user_id = int(payload.get("sub", 0))
    except (HTTPException, TypeError, ValueError):
        return None

    if not jti or user_id <= 0:
        return None

    if RevokedTokenRepository(db).exists(jti):
        return None

    return UserRepository(db).get_by_id(user_id)