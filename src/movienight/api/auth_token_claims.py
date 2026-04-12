from movienight.api.auth_int_claim import read_int_claim
from movienight.api.auth_numeric_subject import read_numeric_subject
from movienight.api.auth_uuid_jti import read_uuid_jti


def read_user_id(payload: dict) -> int:
    return read_numeric_subject(payload)


def read_jti(payload: dict) -> str:
    return read_uuid_jti(payload)


def ensure_time_claims(payload: dict) -> None:
    read_int_claim(payload, "iat")
    read_int_claim(payload, "exp")
