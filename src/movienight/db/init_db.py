from sqlalchemy import select
from sqlalchemy.orm import Session

from movienight.core.clock import utcnow
from movienight.core.config import settings
from movienight.core.security import hash_password
from movienight.db.base import Base
from movienight.db.models import User
from movienight.db.session import SessionLocal, engine


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        _seed_bootstrap_user(db)


def _seed_bootstrap_user(db: Session) -> None:
    users_exist = db.scalar(select(User.id).limit(1)) is not None
    if users_exist:
        return

    bootstrap_user = User(
        username=settings.bootstrap_username.strip(),
        password_hash=hash_password(settings.bootstrap_password),
        created_at=utcnow(),
    )
    db.add(bootstrap_user)
    db.commit()