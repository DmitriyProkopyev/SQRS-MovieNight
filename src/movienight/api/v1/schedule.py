from fastapi import APIRouter, Depends, status

from movienight.api.deps import DbSession, get_current_user
from movienight.schemas.schedule import ScheduleResponse
from movienight.services.schedule_service import ScheduleService

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get(
    "",
    summary="Get weekly room schedule",
    description=(
        "Return the weekly room schedule grouped by room and time slots. "
        "This endpoint is used by the UI to show available and occupied 2-hour screening slots."
    ),
    response_model=ScheduleResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Authentication required."},
    },
)
def get_schedule(
    db: DbSession,
    user=Depends(get_current_user),
) -> ScheduleResponse:
    return ScheduleService(db).get_week_schedule()