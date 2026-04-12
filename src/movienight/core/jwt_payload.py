from datetime import timedelta
from uuid import uuid4

from movienight.core.clock import utcnow
from movienight.core.config import settings


def build_access_token_payload(subject: str) -> dict:
    now = utcnow()
    expires_at = now + timedelta(minutes=settings.jwt_expire_minutes)

    return {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": str(uuid4()),
    }
