from sqlalchemy.orm import Session

from proxy.repositories.user_create import create_user
from proxy.repositories.user_getters import (
    get_user_by_id,
    get_user_by_username,
)


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int):
        return get_user_by_id(self.db, user_id)

    def get_by_username(self, username: str):
        return get_user_by_username(self.db, username)

    def create(self, user):
        return create_user(self.db, user)
