from sqlalchemy.orm import Session

from movienight.repositories.revoked_tokens import RevokedTokenRepository
from movienight.repositories.users import UserRepository
from movienight.schemas.auth import (
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RegisterRequest,
)
from movienight.services.auth_login import login_user
from movienight.services.auth_logout import logout_user
from movienight.services.auth_register import register_user


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.revoked_tokens = RevokedTokenRepository(db)

    def login(
        self,
        payload: LoginRequest,
        current_user=None,
    ) -> LoginResponse:
        return login_user(
            payload=payload,
            current_user=current_user,
            users_repo=self.users,
        )

    def register(
        self,
        payload: RegisterRequest,
        current_user=None,
    ) -> LoginResponse:
        return register_user(
            payload=payload,
            current_user=current_user,
            users_repo=self.users,
        )

    def logout(
        self,
        user,
        token: str | None,
    ) -> MessageResponse:
        return logout_user(
            user=user,
            token=token,
            revoked_tokens_repo=self.revoked_tokens,
        )
