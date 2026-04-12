from fastapi import HTTPException

from movienight.api.auth_user_resolver import resolve_auth_payload


def resolve_optional_payload(credentials):
    if credentials is None:
        return None

    try:
        return resolve_auth_payload(credentials)
    except HTTPException:
        return None
