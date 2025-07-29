from fastapi import APIRouter

from .list_endpoints import router as list_router
from .sync_endpoints import router as sync_router
from .role_endpoints import router as role_router

router = APIRouter()
router.include_router(list_router, prefix="/lists", tags=["lists"])

# Include sync endpoints
router.include_router(sync_router, prefix="/sync", tags=["sync"])

router.include_router(role_router, prefix="/roles", tags=["roles"])

# Include other endpoint routers as they exist
# router.include_router(item_endpoints.router, prefix="/items", tags=["items"])