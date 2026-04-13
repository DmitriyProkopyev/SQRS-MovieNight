import uuid

from movienight.api.auth_malformed_request import raise_malformed_auth_request
from movienight.api.auth_str_claim import read_str_claim


def read_uuid_jti(payload: dict) -> str:
    raw_jti = read_str_claim(payload, "jti")

    try:
        uuid.UUID(raw_jti)
    except (ValueError, TypeError):
        raise_malformed_auth_request()

    return raw_jti
