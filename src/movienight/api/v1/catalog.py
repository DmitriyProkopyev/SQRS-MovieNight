from fastapi import APIRouter, Depends, status

from movienight.api.deps import DbSession, get_current_user
from movienight.schemas.home import HomePageResponse
from movienight.services.home_service import HomeService

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get(
    "",
    summary="Get event catalog",
    description=(
        "Return all proposal cards for catalog browsing. "
        "Unlike Home, this endpoint is focused on card-based navigation through all available events."
    ),
    response_model=HomePageResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Authentication required."},
    },
)
def get_catalog(
    db: DbSession,
    user=Depends(get_current_user),
) -> HomePageResponse:
    return HomeService(db).get_home_page(current_user=user, mine_only=False)