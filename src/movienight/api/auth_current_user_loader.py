from movienight.api.auth_revoked_token_guard import ensure_token_not_revoked
from movienight.api.auth_user_required import require_existing_user


def load_current_user(db, payload):
    user_id = int(payload["sub"])
    jti = payload["jti"]

    ensure_token_not_revoked(
        revoked_tokens=db["revoked_tokens"],
        jti=jti,
    )
    return require_existing_user(
        db["users"].get_by_id(user_id)
    )
