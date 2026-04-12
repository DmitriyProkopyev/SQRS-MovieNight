from movienight.api.auth_claims import extract_jti, extract_user_id
from movienight.api.auth_revocation_guard import ensure_token_not_revoked
from movienight.api.auth_user_loader import load_user_by_id
from movienight.core.jwt_decoder import decode_access_token


def resolve_user_from_token(
    db,
    token: str,
):
    payload = decode_access_token(token)
    jti = extract_jti(payload)
    user_id = extract_user_id(payload)

    ensure_token_not_revoked(db, jti)
    return load_user_by_id(db, user_id)
