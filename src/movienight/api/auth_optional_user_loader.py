from movienight.api.auth_current_user_loader import load_current_user
from movienight.api.auth_optional_credentials import (
    build_optional_credentials,
)
from movienight.api.auth_optional_payload import resolve_optional_payload
from movienight.api.auth_repositories import build_auth_repositories


def load_optional_current_user(
    authorization: str | None,
    db,
):
    credentials = build_optional_credentials(authorization)
    payload = resolve_optional_payload(credentials)
    if payload is None:
        return None

    repositories = build_auth_repositories(db)
    return load_current_user(repositories, payload)
