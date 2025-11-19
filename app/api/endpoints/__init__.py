from fastapi import APIRouter

from .list_endpoints import router as list_router
from .sync_endpoints import router as sync_router
from .user_endpoints import router as user_router
from .project_endpoints import router as project_router
from .step_endpoints import router as step_router

router = APIRouter()
router.include_router(list_router, prefix="/lists", tags=["lists"])
router.include_router(user_router, prefix="/users", tags=["users"])
router.include_router(project_router, prefix="/projects", tags=["projects"])
router.include_router(step_router, prefix="/steps", tags=["steps"])


# Include sync endpoints
router.include_router(sync_router, prefix="/sync", tags=["sync"])

# Include other endpoint routers as they exist
# router.include_router(item_endpoints.router, prefix="/items", tags=["items"])
