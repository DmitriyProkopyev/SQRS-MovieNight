from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials

from movienight.api.auth_payload_validation import validate_auth_payload
from movienight.api.auth_scheme import bearer_scheme
from movienight.api.auth_token_reader import read_bearer_token
from movienight.core.security import decode_access_token


def resolve_auth_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
) -> dict:
    token = read_bearer_token(credentials)
    payload = decode_access_token(token)
    return validate_auth_payload(payload)
