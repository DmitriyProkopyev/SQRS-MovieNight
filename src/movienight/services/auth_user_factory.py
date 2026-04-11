from movienight.core.clock import utcnow
from movienight.core.security import hash_password
from movienight.db.models import User


def build_user_for_registration(
    username: str,
    password: str,
) -> User:
    return User(
        username=username,
        password_hash=hash_password(password),
        created_at=utcnow(),
    )
