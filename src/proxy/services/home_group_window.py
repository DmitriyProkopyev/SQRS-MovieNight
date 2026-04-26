from datetime import datetime

from movienight.core.clock import as_utc
from proxy.db.models import Proposal


def build_group_window(
    component: list[Proposal],
) -> tuple[datetime, datetime]:
    starts_at = min(as_utc(item.starts_at) for item in component)
    ends_at = max(as_utc(item.ends_at) for item in component)
    return starts_at, ends_at
