from fastapi import HTTPException, status


def extract_jti(payload: dict) -> str:
    jti = payload.get("jti")
    if isinstance(jti, str):
        return jti

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token.",
    )
