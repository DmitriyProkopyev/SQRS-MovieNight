from sqlalchemy import select
from sqlalchemy.orm import Session

from proxy.db.models import User


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    statement = select(User).where(User.id == user_id)
    return db.scalar(statement)


def get_user_by_username(
    db: Session,
    username: str,
) -> User | None:
    statement = select(User).where(User.username == username)
    return db.scalar(statement)
