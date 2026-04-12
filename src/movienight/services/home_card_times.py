from datetime import datetime

from movienight.core.clock import as_utc


def normalize_card_times(
    proposal,
    now: datetime,
) -> tuple[datetime, datetime, datetime, datetime]:
    return (
        as_utc(proposal.starts_at),
        as_utc(proposal.ends_at),
        as_utc(proposal.created_at),
        as_utc(now),
    )
