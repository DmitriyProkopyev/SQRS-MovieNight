from datetime import datetime

from sqlalchemy.orm import Session

from proxy.db.models import RevokedToken


def create_revoked_token(
    db: Session,
    jti: str,
    expires_at: datetime,
    reason: str = "logout",
) -> None:
    db.add(
        RevokedToken(
            jti=jti,
            expires_at=expires_at,
            reason=reason,
        )
    )
    db.commit()
