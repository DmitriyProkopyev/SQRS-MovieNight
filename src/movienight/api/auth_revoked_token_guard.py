from fastapi import HTTPException, status


def ensure_token_not_revoked(revoked_tokens, jti: str) -> None:
    if not revoked_tokens.exists(jti):
        return

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token is no longer valid.",
    )
