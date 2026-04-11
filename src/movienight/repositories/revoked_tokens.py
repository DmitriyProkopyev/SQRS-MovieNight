from datetime import datetime

from sqlalchemy.orm import Session

from movienight.repositories.revoked_token_create import (
    create_revoked_token,
)
from movienight.repositories.revoked_token_exists import (
    revoked_token_exists,
)


class RevokedTokenRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def exists(self, jti: str) -> bool:
        return revoked_token_exists(self.db, jti)

    def create(
        self,
        jti: str,
        expires_at: datetime,
        reason: str = "logout",
    ) -> None:
        create_revoked_token(
            db=self.db,
            jti=jti,
            expires_at=expires_at,
            reason=reason,
        )
