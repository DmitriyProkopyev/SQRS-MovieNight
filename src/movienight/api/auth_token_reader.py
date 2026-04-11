from typing import Annotated

from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials

from movienight.api.auth_scheme import bearer_scheme


def read_bearer_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Security(bearer_scheme),
    ] = None,
) -> str | None:
    if credentials is None:
        return None
    return credentials.credentials
