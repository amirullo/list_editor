
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.global_role_schema import GlobalRoleCreate, GlobalRoleUpdate, GlobalRoleInDB
from app.schemas.list_role_schema import ListRoleCreate, ListRoleInDB
from app.schemas.response_schema import ResponseModel
from app.services.global_role_service import GlobalRoleService
from app.services.list_role_service import ListRoleService
from app.api.dependencies import get_global_role_service, get_list_role_service, get_user_id
from app.core.exceptions import PermissionException, NotFoundException, ForbiddenException
from app.models.global_role_model import GlobalRoleType
from app.models.list_role_model import ListRoleType

router = APIRouter()

# Global Role Endpoints

@router.post("/global", response_model=ResponseModel[GlobalRoleInDB])
async def create_global_role(
    role: GlobalRoleCreate,
    global_role_service: GlobalRoleService = Depends(get_global_role_service),
    current_user_id: str = Depends(get_user_id)
):
    try:
        created_role = global_role_service.create_role(current_user_id, role.role_type)
        return ResponseModel(data=created_role, message="Global role created successfully")
    except PermissionException as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/global/{user_id}", response_model=ResponseModel[GlobalRoleInDB])
async def get_global_role(
    user_id: str,
    global_role_service: GlobalRoleService = Depends(get_global_role_service),
    current_user_id: str = Depends(get_user_id)
):
    try:
        role = global_role_service.get_role(user_id)
        if role:
            return ResponseModel(data=role, message="Global role retrieved successfully")
        raise NotFoundException("Global role not found")
    except NotFoundException as nfe:
        raise HTTPException(status_code=404, detail=str(nfe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# @router.put("/global/{user_id}", response_model=ResponseModel[GlobalRoleInDB])
# async def update_global_role(
#     user_id: str,
#     role_update: GlobalRoleUpdate,
#     global_role_service: GlobalRoleService = Depends(get_global_role_service),
#     current_user_id: str = Depends(get_user_id)
# ):
#     try:
#         updated_role = global_role_service.update_role(user_id, role_update.role_type)
#         return ResponseModel(data=updated_role, message="Global role updated successfully")
#     except PermissionException as pe:
#         raise HTTPException(status_code=403, detail=str(pe))
#     except NotFoundException as nfe:
#         raise HTTPException(status_code=404, detail=str(nfe))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# @router.delete("/global/{user_id}", response_model=ResponseModel[dict])
# async def delete_global_role(
#     user_id: str,
#     global_role_service: GlobalRoleService = Depends(get_global_role_service),
#     current_user_id: str = Depends(get_user_id)
# ):
#     try:
#         global_role_service.delete_role(user_id)
#         return ResponseModel(data={"user_id": user_id}, message="Global role deleted successfully")
#     except PermissionException as pe:
#         raise HTTPException(status_code=403, detail=str(pe))
#     except NotFoundException as nfe:
#         raise HTTPException(status_code=404, detail=str(nfe))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# List Role Endpoints

# @router.post("/list", response_model=ResponseModel[ListRoleInDB])
# async def create_list_role(
#     role: ListRoleCreate,
#     list_role_service: ListRoleService = Depends(get_list_role_service),
#     current_user_id: str = Depends(get_user_id)
# ):
#     try:
#         created_role = list_role_service.add_user_to_list(role.user_id, role.list_id, role.role_type)
#         return ResponseModel(data=created_role, message="List role created successfully")
#     except PermissionException as pe:
#         raise HTTPException(status_code=403, detail=str(pe))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.get("/list/{list_id}/{user_id}", response_model=ResponseModel[ListRoleInDB])
async def get_list_role(
    list_id: int,
    user_id: str,
    list_role_service: ListRoleService = Depends(get_list_role_service),
    current_user_id: str = Depends(get_user_id)
):
    try:
        role = list_role_service.get_user_role_in_list(user_id, list_id)
        if role:
            return ResponseModel(data=ListRoleInDB(user_id=user_id, list_id=list_id, role_type=role), message="List role retrieved successfully")
        raise NotFoundException("List role not found")
    except NotFoundException as nfe:
        raise HTTPException(status_code=404, detail=str(nfe))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# @router.put("/list/{list_id}/{user_id}", response_model=ResponseModel[ListRoleInDB])
# async def update_list_role(
#     list_id: int,
#     user_id: str,
#     role_update: ListRoleUpdate,
#     list_role_service: ListRoleService = Depends(get_list_role_service),
#     current_user_id: str = Depends(get_user_id)
# ):
#     try:
#         updated_role = list_role_service.update_user_role_in_list(user_id, list_id, role_update.role_type)
#         return ResponseModel(data=updated_role, message="List role updated successfully")
#     except PermissionException as pe:
#         raise HTTPException(status_code=403, detail=str(pe))
#     except NotFoundException as nfe:
#         raise HTTPException(status_code=404, detail=str(nfe))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# @router.delete("/list/{list_id}/{user_id}", response_model=ResponseModel[dict])
# async def delete_list_role(
#     list_id: int,
#     user_id: str,
#     list_role_service: ListRoleService = Depends(get_list_role_service),
#     current_user_id: str = Depends(get_user_id)
# ):
#     try:
#         list_role_service.remove_user_from_list(user_id, list_id)
#         return ResponseModel(data={"user_id": user_id, "list_id": list_id}, message="List role deleted successfully")
#     except PermissionException as pe:
#         raise HTTPException(status_code=403, detail=str(pe))
#     except NotFoundException as nfe:
#         raise HTTPException(status_code=404, detail=str(nfe))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
