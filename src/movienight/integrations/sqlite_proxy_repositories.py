from dataclasses import dataclass
from datetime import datetime

from movienight.integrations.sqlite_proxy_client import SQLiteProxyClient


@dataclass
class ProxyUserRecord:
    id: int
    username: str
    password_hash: str
    created_at: datetime | None = None


class UserProxyRepository:
    def __init__(self, client: SQLiteProxyClient) -> None:
        self.client = client

    def get_by_id(self, user_id: int):
        data = self.client.get_user_by_id(user_id)
        if not data:
            return None
        return ProxyUserRecord(
            id=data["id"],
            username=data["username"],
            password_hash=data["password_hash"],
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
        )

    def get_by_username(self, username: str):
        data = self.client.get_user_by_username(username)
        if not data:
            return None
        return ProxyUserRecord(
            id=data["id"],
            username=data["username"],
            password_hash=data["password_hash"],
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
        )

    def create(self, user):
        data = self.client.create_user(
            username=user.username,
            password_hash=user.password_hash,
            created_at=user.created_at,
        )
        return ProxyUserRecord(
            id=data["id"],
            username=data["username"],
            password_hash=data["password_hash"],
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
        )


class RevokedTokenProxyRepository:
    def __init__(self, client: SQLiteProxyClient) -> None:
        self.client = client

    def exists(self, jti: str) -> bool:
        return self.client.revoked_token_exists(jti)

    def create(self, jti: str, expires_at: datetime, reason: str = "logout") -> None:
        self.client.create_revoked_token(jti=jti, expires_at=expires_at, reason=reason)