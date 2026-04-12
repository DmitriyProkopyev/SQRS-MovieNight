import jwt

from movienight.core.config import settings


def encode_access_token(payload: dict) -> str:
    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
