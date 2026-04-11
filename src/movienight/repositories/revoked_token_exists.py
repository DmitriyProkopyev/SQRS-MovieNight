from sqlalchemy import select
from sqlalchemy.orm import Session

from movienight.db.models import RevokedToken


def revoked_token_exists(
    db: Session,
    jti: str,
) -> bool:
    statement = select(RevokedToken.id).where(
        RevokedToken.jti == jti,
    )
    return db.scalar(statement) is not None
