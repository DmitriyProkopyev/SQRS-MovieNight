from fastapi.security import HTTPAuthorizationCredentials

from movienight.api.auth_compact_jwt import require_compact_jwt
from movienight.api.auth_credentials_required import require_credentials
from movienight.api.auth_scheme_guard import require_bearer_scheme
from movienight.api.auth_token_presence import require_token_value


def read_bearer_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> str:
    resolved = require_credentials(credentials)
    require_bearer_scheme(resolved.scheme)

    token = require_token_value(resolved.credentials)
    require_compact_jwt(token)
    return token
