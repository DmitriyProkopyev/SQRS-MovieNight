from typing import Annotated

from fastapi import APIRouter, Depends, Security, status
from fastapi.security import HTTPAuthorizationCredentials

from movienight.api.deps import (
    DbSession,
    bearer_scheme,
    get_current_user,
    get_optional_current_user,
)
from movienight.schemas.auth import (
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RegisterRequest,
    UserResponse,
)
from movienight.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    summary="Sign in user",
    description=(
        "Authenticate a user with username and "
        "password and return a JWT access token. "
        "If the user is already authenticated, login must be rejected."
    ),
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Successful login.",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "<JWT_TOKEN>",
                        "token_type": "bearer",
                        "user": {"id": 1, "username": "admin"},
                    }
                }
            },
        },
        400: {
            "description": "User is already authenticated.",
            "content": {
                "application/json": {
                    "example": {"detail": "User is already authenticated."}
                }
            },
        },
        401: {
            "description": "Invalid username or password.",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid login or password."}
                }
            },
        },
    },
)
def login(
    payload: LoginRequest,
    db: DbSession,
    current_user=Depends(get_optional_current_user),
) -> LoginResponse:
    return AuthService(db).login(payload, current_user=current_user)


@router.post(
    "/register",
    summary="Create user account",
    description=(
        "Create a new user account and immediately "
        "return a JWT access token for the created user."
    ),
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "User created successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "<JWT_TOKEN>",
                        "token_type": "bearer",
                        "user": {"id": 5, "username": "new_user"},
                    }
                }
            },
        },
        400: {
            "description": "Registration failed.",
            "content": {
                "application/json": {
                    "examples": {
                        "already_authenticated": {
                            "summary": "Already authenticated",
                            "value": {"detail": (
                                "Log out before "
                                "creating a new account.")},
                        },
                        "username_taken": {
                            "summary": "Username already taken",
                            "value": {"detail": "Username is already taken."},
                        },
                    }
                }
            },
        },
    },
)
def register(
    payload: RegisterRequest,
    db: DbSession,
    current_user=Depends(get_optional_current_user),
) -> LoginResponse:
    return AuthService(db).register(payload, current_user=current_user)


@router.post(
    "/logout",
    summary="Sign out user",
    description="Invalidate the current JWT token so it cannot be used again.",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Successful logout.",
            "content": {
                "application/json": {
                    "example": {"message": "User 'admin' was logged out."}
                }
            },
        },
        401: {
            "description": "Authentication required.",
            "content": {
                "application/json": {
                    "example": {"detail": "Authentication required."}
                }
            },
        },
    },
)
def logout(
    db: DbSession,
    user=Depends(get_current_user),
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Security(bearer_scheme),
    ] = None,
) -> MessageResponse:
    token = credentials.credentials if credentials else None
    return AuthService(db).logout(user=user, token=token)


@router.get(
    "/me",
    summary="Get current user",
    description="Return the currently authenticated user.",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Current user payload.",
            "content": {
                "application/json": {
                    "example": {"id": 1, "username": "admin"}
                }
            },
        },
        401: {
            "description": "Authentication required.",
            "content": {
                "application/json": {
                    "example": {"detail": "Authentication required."}
                }
            },
        },
    },
)
def me(user=Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(user)
