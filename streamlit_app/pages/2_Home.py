import streamlit as st

from frontend.api import ApiError, get_home
from frontend.components import (
    init_app_shell,
    render_group,
    render_sidebar,
    require_auth,
    show_flash,
)
from frontend.state import init_state

init_state()
init_app_shell()
render_sidebar()
require_auth()
show_flash()

st.title("🏠 Home")
st.caption("All movie proposals, conflict groups, votes, and snack reactions.")

refresh_col, _ = st.columns([1, 4])
with refresh_col:
    if st.button("Refresh", key="home-refresh-button", use_container_width=True):
        st.rerun()

try:
    payload = get_home()
except ApiError as exc:
    st.error(str(exc))
    st.stop()

groups = payload.get("groups", [])
current_user = st.session_state["current_user"]["username"]

if not groups:
    st.info("No proposals yet.")
    st.page_link("pages/3_Create_Proposal.py", label="Go to Create Proposal", icon="➕")
    st.stop()

for group in groups:
    render_group(group, current_username=current_user)