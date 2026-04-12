from movienight.api.auth_token_claims import (
    ensure_time_claims,
    read_jti,
    read_user_id,
)


def validate_auth_payload(payload: dict) -> dict:
    ensure_time_claims(payload)
    user_id = read_user_id(payload)
    jti = read_jti(payload)

    return {
        "sub": str(user_id),
        "jti": jti,
        "iat": payload["iat"],
        "exp": payload["exp"],
    }
