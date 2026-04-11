from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from movienight.db.models import RevokedToken


class RevokedTokenRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def exists(self, jti: str) -> bool:
        statement = select(RevokedToken.id).where(RevokedToken.jti == jti)
        return self.db.scalar(statement) is not None

    def create(
        self,
        jti: str,
        expires_at: datetime,
        reason: str = "logout"
    ) -> None:
        if self.exists(jti):
            return
        self.db.add(
            RevokedToken(
                jti=jti,
                expires_at=expires_at,
                reason=reason
            )
        )
        self.db.commit()
