from fastapi.security import HTTPAuthorizationCredentials

from movienight.api.auth_authorization_header import split_authorization_header


def build_optional_credentials(value: str | None):
    parsed = split_authorization_header(value)
    if parsed is None:
        return None

    scheme, token = parsed
    return HTTPAuthorizationCredentials(
        scheme=scheme,
        credentials=token,
    )
