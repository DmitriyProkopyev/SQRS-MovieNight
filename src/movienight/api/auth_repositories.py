from movienight.repositories.revoked_tokens import RevokedTokenRepository
from movienight.repositories.users import UserRepository


def build_auth_repositories(db) -> dict:
    return {
        "users": UserRepository(db),
        "revoked_tokens": RevokedTokenRepository(db),
    }
