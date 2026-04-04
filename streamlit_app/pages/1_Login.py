import streamlit as st

from frontend.api import ApiError, login, register
from frontend.components import init_app_shell, render_sidebar, show_flash
from frontend.state import init_state, is_authenticated, set_flash

init_state()
init_app_shell()
render_sidebar()
show_flash()

st.title("🔐 Login / Registration")

if is_authenticated():
    user = st.session_state.get("current_user") or {}
    st.success(f"You are already logged in as `{user.get('username', 'unknown')}`.")
    st.page_link("pages/2_Home.py", label="Go to Home", icon="🏠")
    st.stop()

login_tab, register_tab = st.tabs(["Login", "Create account"])

with login_tab:
    with st.form("login-form"):
        username = st.text_input("Username", value="")
        password = st.text_input("Password", value="", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        try:
            login(username=username, password=password)
            set_flash("success", f"Logged in as `{username}`.")
            st.switch_page("pages/2_Home.py")
        except ApiError as exc:
            set_flash("error", str(exc))
            st.rerun()

with register_tab:
    with st.form("register-form"):
        new_username = st.text_input("New username", value="")
        new_password = st.text_input("New password", value="", type="password")
        confirm_password = st.text_input("Confirm password", value="", type="password")
        create_submitted = st.form_submit_button("Create account", use_container_width=True)

    if create_submitted:
        if new_password != confirm_password:
            set_flash("error", "Passwords do not match.")
            st.rerun()

        try:
            register(username=new_username, password=new_password)
            set_flash("success", f"Account `{new_username}` created successfully.")
            st.switch_page("pages/2_Home.py")
        except ApiError as exc:
            set_flash("error", str(exc))
            st.rerun()

st.info(
    "The project starts with exactly one bootstrap account from `.env`. "
    "You can create more users through this page."
)