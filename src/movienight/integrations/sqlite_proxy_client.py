from datetime import datetime
from typing import Any

import httpx

from movienight.core.config import settings


class SQLiteProxyClient:
    def __init__(self) -> None:
        self.base_url = settings.sqlite_proxy_url.rstrip("/")

    def _post(self, path: str, payload: dict[str, Any]) -> Any:
        response = httpx.post(f"{self.base_url}{path}", json=payload, timeout=30.0)
        response.raise_for_status()
        return response.json()

    def _get(self, path: str) -> Any:
        response = httpx.get(f"{self.base_url}{path}", timeout=30.0)
        response.raise_for_status()
        return response.json()

    # auth
    def get_user_by_id(self, user_id: int) -> Any:
        return self._post("/internal/auth/get_user_by_id", {"user_id": user_id})

    def get_user_by_username(self, username: str) -> Any:
        return self._post("/internal/auth/get_user_by_username", {"username": username})

    def create_user(self, username: str, password_hash: str, created_at: datetime) -> Any:
        return self._post(
            "/internal/auth/create_user",
            {
                "username": username,
                "password_hash": password_hash,
                "created_at": created_at.isoformat(),
            },
        )

    def revoked_token_exists(self, jti: str) -> bool:
        data = self._post("/internal/auth/revoked_token_exists", {"jti": jti})
        return bool(data["exists"])

    def create_revoked_token(self, jti: str, expires_at: datetime, reason: str = "logout") -> None:
        self._post(
            "/internal/auth/create_revoked_token",
            {
                "jti": jti,
                "expires_at": expires_at.isoformat(),
                "reason": reason,
            },
        )

    # proposals
    def create_proposal(self, payload: dict[str, Any], current_user_id: int) -> Any:
        return self._post(
            "/internal/proposals/create",
            {"payload": payload, "current_user_id": current_user_id},
        )

    def delete_proposal(self, proposal_id: int, current_user_id: int) -> Any:
        return self._post(
            "/internal/proposals/delete",
            {"proposal_id": proposal_id, "current_user_id": current_user_id},
        )

    # votes
    def add_vote(self, proposal_id: int, current_user_id: int) -> Any:
        return self._post(
            "/internal/votes/add",
            {"proposal_id": proposal_id, "current_user_id": current_user_id},
        )

    def remove_vote(self, proposal_id: int, current_user_id: int) -> Any:
        return self._post(
            "/internal/votes/remove",
            {"proposal_id": proposal_id, "current_user_id": current_user_id},
        )

    # reactions
    def add_reaction(self, proposal_id: int, category: str, current_user_id: int) -> Any:
        return self._post(
            "/internal/reactions/add",
            {
                "proposal_id": proposal_id,
                "category": category,
                "current_user_id": current_user_id,
            },
        )

    def remove_reaction(self, proposal_id: int, category: str, current_user_id: int) -> Any:
        return self._post(
            "/internal/reactions/remove",
            {
                "proposal_id": proposal_id,
                "category": category,
                "current_user_id": current_user_id,
            },
        )

    # read models
    def get_home(self, current_user_id: int, mine_only: bool = False) -> Any:
        return self._post(
            "/internal/reads/home",
            {"current_user_id": current_user_id, "mine_only": mine_only},
        )

    def get_catalog(self, current_user_id: int) -> Any:
        return self._post(
            "/internal/reads/catalog",
            {"current_user_id": current_user_id, "mine_only": False},
        )

    def get_schedule(self) -> Any:
        return self._get("/internal/reads/schedule")