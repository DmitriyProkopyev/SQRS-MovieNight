from datetime import UTC, datetime

from fastapi import HTTPException, status

from movienight.core.jwt_decoder import decode_access_token
from movienight.schemas.auth import MessageResponse


def logout_user(
    user,
    token: str | None,
    revoked_tokens_repo,
) -> MessageResponse:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    payload = decode_access_token(token)
    expires_at, jti = extract_logout_token_data(payload)

    revoked_tokens_repo.create(
        jti=jti,
        expires_at=expires_at,
    )
    return MessageResponse(
        message=f"User '{user.username}' was logged out.",
    )


def extract_logout_token_data(payload: dict) -> tuple[datetime, str]:
    try:
        expires_at = datetime.fromtimestamp(
            int(payload["exp"]),
            tz=UTC,
        )
        jti = str(payload["jti"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        ) from exc

    return expires_at, jti
