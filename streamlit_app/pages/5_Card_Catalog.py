import streamlit as st

from frontend.api import ApiError, get_catalog
from frontend.components import (
    format_dt,
    init_app_shell,
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

st.title("🗂️ Card Catalog")
st.caption("Click the background cards to move through the event catalog.")

st.session_state.setdefault("catalog_index", 0)

# CSS only for buttons in the MAIN area, not in the sidebar
st.markdown(
    """
    <style>
    section[data-testid="stMain"] div[data-testid="stButton"] > button.catalog-preview {
        min-height: 270px;
        border-radius: 18px;
        border: 1px solid #4a4a4a;
        background: rgba(255, 255, 255, 0.10);
        color: #eaeaea;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.10);
        padding: 18px 16px;
        text-align: left;
        white-space: pre-wrap;
        line-height: 1.45;
        opacity: 0.58;
        transform: scale(0.94);
        transition: all 0.15s ease-in-out;
    }

    section[data-testid="stMain"] div[data-testid="stButton"] > button.catalog-preview:hover {
        opacity: 0.92;
        transform: scale(0.98);
        border-color: #8a8a8a;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.16);
    }

    section[data-testid="stMain"] div[data-testid="stButton"] > button.catalog-preview:disabled {
        opacity: 0.18;
        background: rgba(245, 245, 245, 0.08);
        border-color: #3a3a3a;
        color: #777777;
    }

    .catalog-main-card {
        border: 1px solid #d9d9d9;
        border-radius: 18px;
        padding: 24px;
        min-height: 340px;
        background: #ffffff;
        color: #1f1f1f;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.10);
    }

    .catalog-badge {
        font-size: 14px;
        opacity: 0.72;
        margin-bottom: 8px;
    }

    .catalog-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 16px;
        line-height: 1.15;
    }

    .catalog-meta {
        margin: 6px 0;
        font-size: 16px;
        line-height: 1.35;
    }

    .catalog-counter {
        text-align: center;
        margin: 8px 0 14px 0;
        opacity: 0.75;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def flatten_cards(groups: list[dict]) -> list[dict]:
    cards: list[dict] = []
    for group in groups:
        for proposal in group.get("proposals", []):
            cards.append(
                {
                    "group_room": group["room"],
                    "group_starts_at": group["starts_at"],
                    "group_ends_at": group["ends_at"],
                    "is_conflict": group["is_conflict"],
                    "winner_proposal_id": group.get("winner_proposal_id"),
                    "proposal": proposal,
                }
            )
    return cards


def preview_label(card: dict | None, side: str) -> str:
    if card is None:
        return ""

    proposal = card["proposal"]
    badge = "🏆" if card["winner_proposal_id"] == proposal["id"] else "🎞️"
    direction = "Previous" if side == "left" else "Next"

    return (
        f"{direction}\n\n"
        f"{badge}  {proposal['movie_title']}\n"
        f"Room: {proposal['room']}\n"
        f"Start: {format_dt(proposal['starts_at'])}\n"
        f"Votes: {proposal['votes_count']}"
    )


def render_main_card(card: dict) -> None:
    proposal = card["proposal"]
    badge = "🏆 Winner" if card["winner_proposal_id"] == proposal["id"] else "🎞️ Event"

    st.markdown(
        f"""
        <div class="catalog-main-card">
            <div class="catalog-badge">{badge}</div>
            <div class="catalog-title">{proposal['movie_title']}</div>
            <div class="catalog-meta"><b>Room:</b> {proposal['room']}</div>
            <div class="catalog-meta"><b>Start:</b> {format_dt(proposal['starts_at'])}</div>
            <div class="catalog-meta"><b>End:</b> {format_dt(proposal['ends_at'])}</div>
            <div class="catalog-meta"><b>Created by:</b> {proposal['created_by']}</div>
            <div class="catalog-meta"><b>Votes:</b> {proposal['votes_count']}</div>
            <div class="catalog-meta"><b>Conflict group:</b> {"Yes" if card["is_conflict"] else "No"}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


try:
    payload = get_catalog()
except ApiError as exc:
    st.error(str(exc))
    st.stop()

cards = flatten_cards(payload.get("groups", []))

if not cards:
    st.info("No events available yet.")
    st.stop()

if st.session_state["catalog_index"] >= len(cards):
    st.session_state["catalog_index"] = max(0, len(cards) - 1)

current_index = st.session_state["catalog_index"]
current_card = cards[current_index]

if len(cards) == 1:
    st.markdown(
        f'<div class="catalog-counter">Card <b>1</b> of <b>1</b></div>',
        unsafe_allow_html=True,
    )
    _, center_col, _ = st.columns([1, 1.45, 1])
    with center_col:
        render_main_card(current_card)
else:
    previous_card = cards[current_index - 1] if current_index > 0 else None
    next_card = cards[current_index + 1] if current_index < len(cards) - 1 else None

    st.markdown(
        f'<div class="catalog-counter">Card <b>{current_index + 1}</b> of <b>{len(cards)}</b></div>',
        unsafe_allow_html=True,
    )

    left_col, center_col, right_col = st.columns([1, 1.45, 1], vertical_alignment="center")

    with left_col:
        left_clicked = st.button(
            preview_label(previous_card, "left"),
            key="catalog-left-preview",
            disabled=previous_card is None,
            use_container_width=True,
        )
        st.markdown(
            """
            <script>
            const buttons = window.parent.document.querySelectorAll('section[data-testid="stMain"] div[data-testid="stButton"] > button');
            if (buttons.length > 0) {
                buttons[buttons.length - 1]?.classList.add("catalog-preview");
            }
            </script>
            """,
            unsafe_allow_html=True,
        )
        if left_clicked:
            st.session_state["catalog_index"] = current_index - 1
            st.rerun()

    with center_col:
        render_main_card(current_card)

    with right_col:
        right_clicked = st.button(
            preview_label(next_card, "right"),
            key="catalog-right-preview",
            disabled=next_card is None,
            use_container_width=True,
        )
        st.markdown(
            """
            <script>
            const buttons = window.parent.document.querySelectorAll('section[data-testid="stMain"] div[data-testid="stButton"] > button');
            if (buttons.length > 0) {
                buttons[buttons.length - 1]?.classList.add("catalog-preview");
            }
            </script>
            """,
            unsafe_allow_html=True,
        )
        if right_clicked:
            st.session_state["catalog_index"] = current_index + 1
            st.rerun()

proposal = current_card["proposal"]
if proposal.get("show_reactions"):
    if proposal.get("reactions"):
        st.subheader("Food reactions")
        chunks = [f"{category}: {total}" for category, total in proposal["reactions"].items()]
        st.write(" | ".join(chunks))
    else:
        st.caption("No food reactions for this event yet.")
else:
    st.caption(
        "Snack reactions are available only for the selected winner during the final hour before the event."
    )