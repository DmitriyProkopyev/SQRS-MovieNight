import uuid

from fastapi import HTTPException, status


def read_user_id(payload: dict) -> int:
    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.isdecimal():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed authentication request.",
        )

    user_id = int(subject)
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed authentication request.",
        )

    return user_id


def read_jti(payload: dict) -> str:
    raw_jti = payload.get("jti")
    if not isinstance(raw_jti, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed authentication request.",
        )

    try:
        uuid.UUID(raw_jti)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed authentication request.",
        ) from exc

    return raw_jti


def ensure_time_claims(payload: dict) -> None:
    iat = payload.get("iat")
    exp = payload.get("exp")

    if not isinstance(iat, int) or not isinstance(exp, int):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed authentication request.",
        )