from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from movienight.core.clock import utcnow
from movienight.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from movienight.db.models import User
from movienight.repositories.revoked_tokens import RevokedTokenRepository
from movienight.repositories.users import UserRepository
from movienight.schemas.auth import (
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RegisterRequest,
    UserResponse,
)


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.revoked_tokens = RevokedTokenRepository(db)

    def login(
        self,
        payload: LoginRequest,
        current_user=None
    ) -> LoginResponse:
        if current_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already authenticated.",
            )

        user = self.users.get_by_username(payload.username.strip())
        if user is None or not verify_password(
            payload.password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect login or password",
            )

        token = create_access_token(subject=str(user.id))
        return LoginResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )

    def register(
        self,
        payload: RegisterRequest,
        current_user=None
    ) -> LoginResponse:
        if current_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Log out before creating a new account.",
            )

        username = payload.username.strip()
        if not username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username cannot be empty.",
            )

        existing_user = self.users.get_by_username(username)
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already taken.",
            )

        user = self.users.create(
            User(
                username=username,
                password_hash=hash_password(payload.password),
                created_at=utcnow(),
            )
        )

        token = create_access_token(subject=str(user.id))
        return LoginResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )

    def logout(self, user, token: str | None) -> MessageResponse:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required.",
            )

        payload = decode_access_token(token)

        try:
            expires_at = datetime.fromtimestamp(int(payload["exp"]), tz=UTC)
            jti = str(payload["jti"])
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token.",
            ) from exc

        self.revoked_tokens.create(jti=jti, expires_at=expires_at)
        return MessageResponse(
            message=f"User '{user.username}' was logged out."
        )
