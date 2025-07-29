from fastapi import APIRouter, Depends
from typing import Dict

from app.models.role_model import RoleType
from app.schemas.role_schema import RoleCreate, RoleInDB
from app.schemas.response_schema import ResponseModel
from app.services.role_service import RoleService
from app.api.dependencies import get_role_service, get_user_id

router = APIRouter()

@router.post("/", response_model=ResponseModel[RoleInDB])
def create_role(
    role_create: RoleCreate,
    role_service: RoleService = Depends(get_role_service),
    user_id: str = Depends(get_user_id)
):
    """
    Create a role for the user
    """
    role = role_service.create_role(user_id, role_create.role_type)
    return ResponseModel(
        status="success",
        message=f"Role {role.role_type.value} assigned successfully",
        data=role
    )

@router.get("/", response_model=ResponseModel[Dict])
def get_current_role(
    role_service: RoleService = Depends(get_role_service),
    user_id: str = Depends(get_user_id)
):
    """
    Get the current role of the user
    """
    role = role_service.get_role(user_id)
    
    if role:
        return ResponseModel(
            status="success",
            message="Current role retrieved successfully",
            data={"role": role.role_type.value, "user_id": user_id}
        )
    else:
        return ResponseModel(
            status="success",
            message="No role assigned",
            data={"role": None, "user_id": user_id}
        )