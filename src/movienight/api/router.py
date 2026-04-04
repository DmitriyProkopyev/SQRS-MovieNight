from fastapi import APIRouter

from movienight.api.v1.auth import router as auth_router
from movienight.api.v1.home import router as home_router
from movienight.api.v1.proposals import router as proposals_router
from movienight.api.v1.reactions import router as reactions_router
from movienight.api.v1.votes import router as votes_router
from movienight.api.v1.catalog import router as catalog_router
from movienight.api.v1.schedule import router as schedule_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(home_router)
api_router.include_router(proposals_router)
api_router.include_router(votes_router)
api_router.include_router(reactions_router)
api_router.include_router(catalog_router)
api_router.include_router(schedule_router)
