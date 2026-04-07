from fastapi import APIRouter, Depends, status

from movienight.api.deps import DbSession, get_current_user
from movienight.schemas.home import HomePageResponse
from movienight.services.home_service import HomeService

router = APIRouter(prefix="/home", tags=["home"])


@router.get(
    "",
    summary="Get home page data",
    description=(
        "Return grouped proposals for the main page, including room, time slot, voting state, "
        "conflict metadata, winner information, and reaction visibility flags. "
        "Snack reactions are returned only when they are actually visible and available."
    ),
    response_model=HomePageResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Authentication required."},
    },
)
def get_home(db: DbSession, user=Depends(get_current_user)) -> HomePageResponse:
    return HomeService(db).get_home_page(current_user=user)