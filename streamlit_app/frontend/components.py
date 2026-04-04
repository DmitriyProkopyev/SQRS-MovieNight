from datetime import datetime

import streamlit as st

from frontend.api import (
    ApiError,
    add_reaction,
    add_vote,
    delete_proposal,
    logout,
    refresh_current_user,
    remove_reaction,
    remove_vote,
)
from frontend.config import EMOJI_BY_CATEGORY, FOOD_CATEGORIES
from frontend.state import clear_flash, init_state, is_authenticated, set_flash


def init_app_shell() -> None:
    init_state()
    refresh_current_user()


def show_flash() -> None:
    flash = st.session_state.get("flash")
    if not flash:
        return

    level = flash["level"]
    message = flash["message"]

    if level == "success":
        st.success(message)
    elif level == "warning":
        st.warning(message)
    else:
        st.error(message)

    clear_flash()


def render_sidebar() -> None:
    st.sidebar.title("Movie Night")

    current_value = st.session_state.get("api_base", "")
    st.session_state["api_base"] = st.sidebar.text_input(
        "Backend API URL",
        value=current_value,
    )

    current_user = st.session_state.get("current_user")
    if current_user:
        st.sidebar.success(f"Logged in as `{current_user['username']}`")
    else:
        st.sidebar.warning("Not authenticated")

    st.sidebar.page_link("app.py", label="Overview", icon="🎬")
    st.sidebar.page_link("pages/1_Login.py", label="Login", icon="🔐")
    st.sidebar.page_link("pages/2_Home.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/3_Create_Proposal.py", label="Create Proposal", icon="➕")
    st.sidebar.page_link("pages/4_Profile.py", label="Profile", icon="👤")
    st.sidebar.page_link("pages/5_Card_Catalog.py", label="Card Catalog", icon="🗂️")

    if current_user and st.sidebar.button(
        "Logout",
        key="sidebar-logout-button",
        use_container_width=True,
    ):
        logout()
        set_flash("success", "Logged out successfully.")
        st.switch_page("pages/1_Login.py")


def require_auth() -> None:
    if not is_authenticated():
        st.warning("You need to log in first.")
        st.page_link("pages/1_Login.py", label="Go to Login", icon="🔐")
        st.stop()


def format_dt(value: str) -> str:
    parsed = datetime.fromisoformat(value)
    return parsed.strftime("%Y-%m-%d %H:%M UTC")


def render_reactions_block(proposal: dict) -> None:
    if not proposal.get("show_reactions", False):
        st.caption(
            "Snack reactions become available only for the selected winner during the final hour before the event."
        )
        return

    reactions = proposal.get("reactions") or {}
    my_reactions = set(proposal.get("my_reactions", []))

    if reactions:
        chunks = []
        for category, total in reactions.items():
            emoji = EMOJI_BY_CATEGORY.get(category, "🍽️")
            chunks.append(f"{emoji} {category}: {total}")
        st.caption(" | ".join(chunks))
    else:
        st.caption("No food reactions yet.")

    selected_category = st.selectbox(
        "Food category",
        options=FOOD_CATEGORIES,
        format_func=lambda item: f"{EMOJI_BY_CATEGORY[item]} {item}",
        key=f"reaction-select-{proposal['id']}",
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Add reaction",
            key=f"reaction-add-{proposal['id']}",
            use_container_width=True,
            disabled=not proposal.get("can_add_reaction", False),
        ):
            try:
                add_reaction(proposal["id"], selected_category)
                set_flash("success", "Reaction added.")
                st.rerun()
            except ApiError as exc:
                set_flash("error", str(exc))
                st.rerun()

    with col2:
        can_remove_selected = (
            selected_category in my_reactions and proposal.get("can_remove_reaction", False)
        )
        if st.button(
            "Remove reaction",
            key=f"reaction-remove-{proposal['id']}",
            use_container_width=True,
            disabled=not can_remove_selected,
        ):
            try:
                remove_reaction(proposal["id"], selected_category)
                set_flash("success", "Reaction removed.")
                st.rerun()
            except ApiError as exc:
                set_flash("error", str(exc))
                st.rerun()

def render_proposal_card(proposal: dict, current_username: str) -> None:
    title = proposal["movie_title"]
    if proposal.get("is_winner"):
        title += " 🏆"

    st.markdown(f"### {title}")
    st.write(f"**Room:** {proposal['room']}")
    st.write(f"**Start:** {format_dt(proposal['starts_at'])}")
    st.write(f"**End:** {format_dt(proposal['ends_at'])}")
    st.write(f"**Author:** `{proposal['created_by']}`")
    st.write(f"**Votes:** {proposal['votes_count']}")

    if proposal.get("is_past"):
        st.warning("This proposal is already in the past.")

    action_col1, action_col2 = st.columns(2)

    with action_col1:
        vote_label = "Remove vote" if proposal["my_vote"] else "Vote"
        vote_allowed = proposal["can_unvote"] if proposal["my_vote"] else proposal["can_vote"]

        if st.button(
            vote_label,
            key=f"vote-{proposal['id']}",
            use_container_width=True,
            disabled=not vote_allowed,
        ):
            try:
                if proposal["my_vote"]:
                    remove_vote(proposal["id"])
                else:
                    add_vote(proposal["id"])
                set_flash("success", "Vote updated.")
                st.rerun()
            except ApiError as exc:
                set_flash("error", str(exc))
                st.rerun()

    with action_col2:
        if st.button(
            "Delete proposal",
            key=f"delete-{proposal['id']}",
            use_container_width=True,
            disabled=not proposal.get("can_delete", False),
        ):
            try:
                delete_proposal(proposal["id"])
                set_flash("success", "Proposal deleted.")
                st.rerun()
            except ApiError as exc:
                set_flash("error", str(exc))
                st.rerun()

    render_reactions_block(proposal)
    st.divider()


def render_group(group: dict, current_username: str) -> None:
    title = (
        f"{group['room']} | "
        f"{format_dt(group['starts_at'])} → {format_dt(group['ends_at'])}"
    )

    with st.expander(title, expanded=True):
        if group["is_conflict"] and group.get("winner_proposal_id") is None:
            st.warning("Conflict group. Voting is still open.")
        elif group["is_conflict"] and group.get("winner_proposal_id") is not None:
            st.success(
                f"Conflict group closed. Winner proposal ID: {group['winner_proposal_id']}"
            )
        else:
            st.info("Single proposal.")

        for proposal in group["proposals"]:
            render_proposal_card(proposal, current_username=current_username)