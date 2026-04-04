import streamlit as st

from frontend.config import DEFAULT_API_BASE


def init_state() -> None:
    defaults = {
        "api_base": DEFAULT_API_BASE,
        "access_token": None,
        "current_user": None,
        "flash": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def set_flash(level: str, message: str) -> None:
    st.session_state["flash"] = {
        "level": level,
        "message": message,
    }


def clear_flash() -> None:
    st.session_state["flash"] = None


def save_auth(access_token: str, user: dict) -> None:
    st.session_state["access_token"] = access_token
    st.session_state["current_user"] = user


def clear_auth() -> None:
    st.session_state["access_token"] = None
    st.session_state["current_user"] = None


def is_authenticated() -> bool:
    return bool(st.session_state.get("access_token"))


def auth_headers() -> dict[str, str]:
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}