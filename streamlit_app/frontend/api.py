from datetime import datetime
from typing import Any

import requests
import streamlit as st

from frontend.state import auth_headers, clear_auth, save_auth


class ApiError(Exception):
    pass


def _build_url(path: str) -> str:
    base = st.session_state["api_base"].rstrip("/")
    return f"{base}{path}"


def _extract_error(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text or f"HTTP {response.status_code}"

    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail

        message = payload.get("message")
        if isinstance(message, str):
            return message

    return str(payload)


def request(
    method: str,
    path: str,
    *,
    json_body: dict[str, Any] | None = None,
    use_auth: bool = True,
) -> dict[str, Any]:
    headers: dict[str, str] = {}
    if use_auth:
        headers.update(auth_headers())

    try:
        response = requests.request(
            method=method,
            url=_build_url(path),
            headers=headers,
            json=json_body,
            timeout=15,
        )
    except requests.RequestException as exc:
        raise ApiError(f"Cannot connect to backend: {exc}") from exc

    if response.status_code == 401:
        clear_auth()

    if response.status_code >= 400:
        raise ApiError(_extract_error(response))

    if not response.content:
        return {}

    try:
        return response.json()
    except ValueError:
        return {}


def login(username: str, password: str) -> dict[str, Any]:
    data = request(
        "POST",
        "/auth/login",
        json_body={"username": username, "password": password},
        use_auth=False,
    )
    save_auth(data["access_token"], data["user"])
    return data


def register(username: str, password: str) -> dict[str, Any]:
    data = request(
        "POST",
        "/auth/register",
        json_body={"username": username, "password": password},
        use_auth=False,
    )
    save_auth(data["access_token"], data["user"])
    return data


def logout() -> None:
    try:
        request("POST", "/auth/logout")
    except ApiError:
        pass
    clear_auth()


def get_me() -> dict[str, Any]:
    return request("GET", "/auth/me")


def refresh_current_user() -> None:
    token = st.session_state.get("access_token")
    if not token:
        st.session_state["current_user"] = None
        return

    try:
        st.session_state["current_user"] = get_me()
    except ApiError:
        clear_auth()


def get_home() -> dict[str, Any]:
    return request("GET", "/home")


def get_catalog() -> dict[str, Any]:
    return request("GET", "/catalog")


def get_schedule() -> dict[str, Any]:
    return request("GET", "/schedule")


def create_proposal(
    room: str,
    movie_title: str,
    starts_at: datetime,
    ends_at: datetime,
) -> dict[str, Any]:
    return request(
        "POST",
        "/proposals",
        json_body={
            "room": room,
            "movie_title": movie_title,
            "starts_at": starts_at.isoformat(),
            "ends_at": ends_at.isoformat(),
        },
    )


def delete_proposal(proposal_id: int) -> dict[str, Any]:
    return request("DELETE", f"/proposals/{proposal_id}")


def add_vote(proposal_id: int) -> dict[str, Any]:
    return request("POST", f"/proposals/{proposal_id}/votes")


def remove_vote(proposal_id: int) -> dict[str, Any]:
    return request("DELETE", f"/proposals/{proposal_id}/votes")


def add_reaction(proposal_id: int, category: str) -> dict[str, Any]:
    return request(
        "POST",
        f"/proposals/{proposal_id}/reactions",
        json_body={"category": category},
    )


def remove_reaction(proposal_id: int, category: str) -> dict[str, Any]:
    return request("DELETE", f"/proposals/{proposal_id}/reactions/{category}")