from fastapi import APIRouter, HTTPException, status

from movienight.db.models import User
from proxy.api.deps import DbSession
from proxy.api.models import (
    InternalRevokedTokenCreateRequest,
    InternalRevokedTokenExistsRequest,
    InternalUserCreateRequest,
    InternalUserIdRequest,
    InternalUsernameRequest,
)
from proxy.repositories.revoked_tokens import RevokedTokenRepository
from proxy.repositories.users import UserRepository

router = APIRouter()


@router.post("/get_user_by_id")
def get_user_by_id(payload: InternalUserIdRequest, db: DbSession):
    user = UserRepository(db).get_by_id(payload.user_id)
    return user


@router.post("/get_user_by_username")
def get_user_by_username(payload: InternalUsernameRequest, db: DbSession):
    user = UserRepository(db).get_by_username(payload.username)
    return user


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
def create_user(payload: InternalUserCreateRequest, db: DbSession):
    user = User(
        username=payload.username,
        password_hash=payload.password_hash,
        created_at=payload.created_at,
    )
    return UserRepository(db).create(user)


@router.post("/revoked_token_exists")
def revoked_token_exists(payload: InternalRevokedTokenExistsRequest, db: DbSession):
    exists = RevokedTokenRepository(db).exists(payload.jti)
    return {"exists": exists}


@router.post("/create_revoked_token", status_code=status.HTTP_201_CREATED)
def create_revoked_token(payload: InternalRevokedTokenCreateRequest, db: DbSession):
    RevokedTokenRepository(db).create(
        jti=payload.jti,
        expires_at=payload.expires_at,
        reason=payload.reason,
    )
    return {"message": "Revoked token created."}