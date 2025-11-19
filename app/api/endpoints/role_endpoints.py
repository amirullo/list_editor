from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.schemas.global_role_schema import GlobalRoleCreate, GlobalRoleInDB, GlobalRoleResponse
from app.services.global_role_service import GlobalRoleService
from app.api.dependencies import get_global_role_service, get_current_user_id
# from uuid import UUID # Removed UUID import
from app.utils.logger import logger # Import logger

router = APIRouter()

@router.post("/roles/global", response_model=GlobalRoleResponse, status_code=status.HTTP_201_CREATED)
def create_global_role(
    global_role_create: GlobalRoleCreate,
    user_internal_id: int = Depends(get_current_user_id), # Changed type to int
    global_role_service: GlobalRoleService = Depends(get_global_role_service)
):
    """
    Create or update a global role for the authenticated user.
    """
    logger.info(f"create_global_role: user_internal_id={user_internal_id}, role_type={global_role_create.role}") # Changed to global_role_create.role
    try:
        role = global_role_service.create_role(user_internal_id, global_role_create.role) # Changed to global_role_create.role
        return GlobalRoleResponse(
            message="Global role created/updated successfully",
            data=GlobalRoleInDB.model_validate(role)
        )
    except Exception as e:
        logger.error(f"create_global_role: Error creating/updating global role: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/roles/global/{target_user_internal_id}", response_model=GlobalRoleResponse)
def get_global_role(
    target_user_internal_id: int, # Changed type to int
    user_internal_id: int = Depends(get_current_user_id), # Authenticated user, changed type to int
    global_role_service: GlobalRoleService = Depends(get_global_role_service)
):
    """
    Get the global role for a specific user.
    """
    logger.info(f"get_global_role: target_user_internal_id={target_user_internal_id}, authenticated_user_internal_id={user_internal_id}")
    # In a real application, you might want to add authorization here
    # to ensure that the authenticated user has permission to view
    # another user's global role. For now, we'll allow it.
    
    role = global_role_service.get_role(target_user_internal_id)
    if not role:
        logger.warning(f"get_global_role: Global role not found for user {target_user_internal_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Global role not found for this user")
    
    return GlobalRoleResponse(
        message="Global role retrieved successfully",
        data=GlobalRoleInDB.model_validate(role)
    )
