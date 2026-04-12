from fastapi import Depends, Request
from sqlalchemy.orm import Session

from movienight.api.auth_current_user_loader import load_current_user
from movienight.api.auth_optional_user_loader import (
    load_optional_current_user,
)
from movienight.api.auth_repositories import build_auth_repositories
from movienight.api.auth_user_resolver import resolve_auth_payload
from movienight.db.session import get_db


def get_current_user(
    db: Session = Depends(get_db),
    payload: dict = Depends(resolve_auth_payload),
):
    repositories = build_auth_repositories(db)
    return load_current_user(repositories, payload)


def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    authorization = request.headers.get("authorization")
    return load_optional_current_user(authorization, db)
