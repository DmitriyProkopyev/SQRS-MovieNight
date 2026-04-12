from movienight.core.jwt_decoder import decode_access_token
from movienight.core.jwt_encoder import encode_access_token
from movienight.core.jwt_payload import build_access_token_payload
from movienight.core.password_hasher import (
    hash_password,
    verify_password,
)


def create_access_token(subject: str) -> str:
    payload = build_access_token_payload(subject)
    return encode_access_token(payload)


__all__ = [
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "verify_password",
]
