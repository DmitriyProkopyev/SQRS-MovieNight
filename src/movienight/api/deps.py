from typing import Annotated

from fastapi import Depends

from movienight.api.auth_required_user import (
    get_current_user,
    get_optional_current_user,
)
from movienight.api.auth_scheme import bearer_scheme
from movienight.api.db_deps import get_db

DbSession = Annotated[object, Depends(get_db)]
CurrentUser = Annotated[object, Depends(get_current_user)]

__all__ = [
    "get_db",
    "DbSession",
    "bearer_scheme",
    "get_current_user",
    "get_optional_current_user",
    "CurrentUser",
]