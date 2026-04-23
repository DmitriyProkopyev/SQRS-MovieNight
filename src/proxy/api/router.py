from fastapi import APIRouter

from proxy.api.internal_auth import router as auth_router
from proxy.api.internal_proposals import router as proposals_router
from proxy.api.internal_votes import router as votes_router
from proxy.api.internal_reactions import router as reactions_router
from proxy.api.internal_reads import router as reads_router

router = APIRouter(prefix="/internal")
router.include_router(auth_router, prefix="/auth", tags=["internal-auth"])
router.include_router(proposals_router, prefix="/proposals", tags=["internal-proposals"])
router.include_router(votes_router, prefix="/votes", tags=["internal-votes"])
router.include_router(reactions_router, prefix="/reactions", tags=["internal-reactions"])
router.include_router(reads_router, prefix="/reads", tags=["internal-reads"])