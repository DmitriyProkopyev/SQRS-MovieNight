from datetime import UTC, datetime, timedelta

import streamlit as st

from frontend.api import ApiError, create_proposal
from frontend.components import init_app_shell, render_sidebar, require_auth, show_flash
from frontend.config import ROOM_OPTIONS
from frontend.state import init_state, set_flash

init_state()
init_app_shell()
render_sidebar()
require_auth()
show_flash()

st.title("➕ Create Proposal")
st.caption("Create a new movie screening proposal using fixed 2-hour slots.")

slot_options = [f"{hour:02d}:00" for hour in range(0, 24, 2)]

now_utc = datetime.now(UTC)
rounded_hour = (now_utc.hour // 2) * 2
default_slot = f"{rounded_hour:02d}:00"
if default_slot not in slot_options:
    default_slot = "00:00"

with st.form("create-proposal-form"):
    room = st.selectbox("Room", options=ROOM_OPTIONS)
    movie_title = st.text_input("Movie title", value="Interstellar")
    start_date = st.date_input("Start date (UTC)", value=(now_utc + timedelta(days=1)).date())
    start_time_label = st.selectbox(
        "Start time (UTC)",
        options=slot_options,
        index=slot_options.index(default_slot),
    )

    submitted = st.form_submit_button("Create proposal", use_container_width=True)

if submitted:
    start_hour = int(start_time_label.split(":")[0])
    starts_at = datetime.combine(
        start_date,
        datetime.min.time().replace(hour=start_hour),
    ).replace(tzinfo=UTC)
    ends_at = starts_at + timedelta(hours=2)

    try:
        create_proposal(
            room=room,
            movie_title=movie_title.strip(),
            starts_at=starts_at,
            ends_at=ends_at,
        )
        set_flash("success", "Proposal created successfully.")
        st.switch_page("pages/2_Home.py")
    except ApiError as exc:
        set_flash("error", str(exc))
        st.rerun()