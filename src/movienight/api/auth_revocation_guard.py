from fastapi import HTTPException, status

from movienight.repositories.revoked_tokens import RevokedTokenRepository


def ensure_token_not_revoked(db, jti: str) -> None:
    if RevokedTokenRepository(db).exists(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked.",
        )
