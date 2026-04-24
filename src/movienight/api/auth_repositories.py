from movienight.integrations.sqlite_proxy_repositories import (
    RevokedTokenProxyRepository,
    UserProxyRepository,
)


def build_auth_repositories(db) -> dict:
    return {
        "users": UserProxyRepository(db),
        "revoked_tokens": RevokedTokenProxyRepository(db),
    }