from fastapi import APIRouter, HTTPException

from proxy.api.deps import DbSession
from proxy.api.models import InternalHomeRequest
from proxy.repositories.users import UserRepository
from proxy.services.home_service import HomeService
from proxy.services.schedule_service import ScheduleService

router = APIRouter()


@router.post("/home")
def get_home(payload: InternalHomeRequest, db: DbSession):
    current_user = UserRepository(db).get_by_id(payload.current_user_id)
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return HomeService(db).get_home_page(
        current_user=current_user,
        mine_only=payload.mine_only,
    )


@router.post("/catalog")
def get_catalog(payload: InternalHomeRequest, db: DbSession):
    current_user = UserRepository(db).get_by_id(payload.current_user_id)
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return HomeService(db).get_home_page(
        current_user=current_user,
        mine_only=False,
    )


@router.get("/schedule")
def get_schedule(db: DbSession):
    return ScheduleService(db).get_week_schedule()