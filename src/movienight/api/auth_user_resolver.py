from fastapi import Depends

from movienight.api.auth_identity_from_token import resolve_user_from_token
from movienight.api.auth_required_user import require_authenticated_user
from movienight.api.auth_token_reader import read_bearer_token
from movienight.api.db_deps import DbSession


def get_optional_current_user(
    db: DbSession,
    token: str | None = Depends(read_bearer_token),
):
    if not token:
        return None

    return resolve_user_from_token(db, token)


def get_current_user(
    user=Depends(get_optional_current_user),
):
    return require_authenticated_user(user)
