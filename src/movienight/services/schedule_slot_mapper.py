from movienight.schemas.schedule import ScheduleSlot


def map_schedule_slot(
    slot: dict,
    proposal_titles: list[str],
) -> ScheduleSlot:
    return ScheduleSlot(
        slot_date=slot["slot_date"],
        day_name=slot["day_name"],
        day_label=slot["day_label"],
        time_label=slot["time_label"],
        display_label=slot["display_label"],
        start_at=slot["start_at"],
        end_at=slot["end_at"],
        occupied=bool(proposal_titles),
        proposal_titles=proposal_titles,
    )
