from movienight.db.models import Proposal
from movienight.services.schedule_exceptions import raise_bad_request

_MAX_OVERLAPS = 5


def ensure_not_too_many_conflicts(
    conflicts: list[Proposal],
) -> None:
    if len(conflicts) >= _MAX_OVERLAPS:
        raise_bad_request(
            "Too many overlapping proposals already exist "
            "in this room."
        )
