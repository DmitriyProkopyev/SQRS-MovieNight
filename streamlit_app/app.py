import streamlit as st

from frontend.components import init_app_shell, render_sidebar, show_flash
from frontend.state import init_state, is_authenticated

st.set_page_config(
    page_title="Movie Night",
    page_icon="🎬",
    layout="wide",
)

init_state()
init_app_shell()
render_sidebar()
show_flash()

st.title("🎬 Movie Night")
st.caption("Minimal frontend for manual testing of the service.")

left, right = st.columns([2, 1])

with left:
    st.subheader("What is available right now")
    st.markdown(
        """
        - Login and logout
        - User registration
        - Home page with all proposals and conflict groups
        - Free-form proposal creation up to 4 hours
        - Vote / unvote
        - Add / remove food reactions
        - Delete own proposals
        - Card Catalog page for browsing all event cards
        """
    )

    st.subheader("Navigation")
    st.page_link("pages/1_Login.py", label="Open Login page", icon="🔐")
    st.page_link("pages/2_Home.py", label="Open Home page", icon="🏠")
    st.page_link("pages/3_Create_Proposal.py", label="Open Create Proposal page", icon="➕")
    st.page_link("pages/4_Profile.py", label="Open Profile page", icon="👤")
    st.page_link("pages/5_Card_Catalog.py", label="Open Card Catalog", icon="🗂️")

with right:
    st.subheader("Session status")
    if is_authenticated():
        user = st.session_state.get("current_user") or {}
        st.success(f"Logged in as `{user.get('username', 'unknown')}`")
    else:
        st.warning("Not authenticated yet.")

    st.info(
        "Run backend first, then open Login page and sign in. "
        "After that, use Home, Create Proposal, and Card Catalog pages."
    )