from datetime import datetime


def build_time_label(
    start_at: datetime,
    end_at: datetime,
) -> str:
    return (
        f"{start_at.strftime('%H:%M')}"
        f"–{end_at.strftime('%H:%M')}"
    )


def build_display_label(
    slot_date_label: str,
    time_label: str,
) -> str:
    return f"{slot_date_label} | {time_label}"
