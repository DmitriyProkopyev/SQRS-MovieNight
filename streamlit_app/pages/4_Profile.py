import streamlit as st

from frontend.api import ApiError, get_me, logout, refresh_current_user
from frontend.components import init_app_shell, render_sidebar, require_auth, show_flash
from frontend.state import init_state, set_flash

init_state()
init_app_shell()
render_sidebar()
require_auth()
show_flash()

st.title("👤 Profile")
st.caption("Current session, token, and backend connection state.")

user = st.session_state.get("current_user") or {}
token = st.session_state.get("access_token") or ""

st.subheader("Current user")
st.json(user)

st.subheader("Access token")
st.code(token if token else "No token")

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "Refresh profile",
        key="profile-refresh-button",
        use_container_width=True,
    ):
        try:
            refresh_current_user()
            set_flash("success", "Profile refreshed.")
            st.rerun()
        except ApiError as exc:
            set_flash("error", str(exc))
            st.rerun()

with col2:
    if st.button(
        "Logout",
        key="profile-logout-button",
        use_container_width=True,
    ):
        logout()
        set_flash("success", "Logged out successfully.")
        st.switch_page("pages/1_Login.py")

st.subheader("Backend info")
st.write(f"API base: `{st.session_state['api_base']}`")

if st.button(
    "Call /auth/me directly",
    key="profile-call-me-button",
    use_container_width=True,
):
    try:
        payload = get_me()
        st.success("Request successful.")
        st.json(payload)
    except ApiError as exc:
        st.error(str(exc))