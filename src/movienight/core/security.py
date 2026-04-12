from movienight.core.jwt_encoder import encode_access_token
from movienight.core.jwt_payload import build_access_token_payload


def create_access_token(subject: str) -> str:
    payload = build_access_token_payload(subject)
    return encode_access_token(payload)
