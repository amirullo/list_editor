
from fastapi import APIRouter, Depends, status
from typing import List as TypeList, Dict, Any, Optional
from app.schemas.list_schema import ListCreate, ListUpdate, ListInDB, ListAddUser, ListRemoveUser
from app.schemas.item_schema import ItemCreate, ItemUpdate, ItemInDB
from app.schemas.response_schema import ResponseModel, StatusMessage
from app.services.list_service import ListService
from app.services.item_service import ItemService
from app.services.lock_service import LockService
from app.services.user_service import UserService
from app.api.dependencies import (
    get_list_service,
    get_item_service,
    get_lock_service,
    get_current_user_id,
    require_list_access,
    require_list_creator,
    get_user_service
)
from app.core.exceptions import NotFoundException
from app.models.global_role_model import GlobalRoleType
from pydantic import BaseModel
from app.utils.logger import logger

class CreateListRequest(BaseModel):
    list_create: ListCreate
    items: Optional[TypeList[ItemCreate]] = None

router = APIRouter()

@router.post("/", response_model=ResponseModel[ListInDB])
async def create_list(
    request: CreateListRequest,
    list_service: ListService = Depends(get_list_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    new_list = list_service.create_list(request.list_create,
                                        user_internal_id,
                                        request.items)
    return ResponseModel(data=new_list, message="List created successfully")

@router.get("/", response_model=ResponseModel[TypeList[ListInDB]])
def get_all_lists(
    list_service: ListService = Depends(get_list_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    lists = list_service.get_all_lists(user_internal_id)
    return ResponseModel(data=lists, message="Lists retrieved successfully")

@router.get("/{list_id}", response_model=ResponseModel[ListInDB])
async def get_list(
    list_id: int,
    list_service: ListService = Depends(get_list_service),
    user_internal_id: int = Depends(get_current_user_id),
    _: None = Depends(require_list_access)
):
    db_list = list_service.get_list(list_id, user_internal_id)
    return ResponseModel(data=db_list, message="List retrieved successfully")

@router.put("/{list_id}", response_model=ResponseModel[ListInDB])
async def update_list(
    list_id: int,
    list_update: ListUpdate,
    list_service: ListService = Depends(get_list_service),
    user_internal_id: int = Depends(get_current_user_id),
    _: None = Depends(require_list_access)
):
    updated_list = list_service.update_list(list_id, list_update, user_internal_id)
    return ResponseModel(data=updated_list, message="List updated successfully")

@router.delete("/{list_id}", response_model=ResponseModel[dict])
async def delete_list(
    list_id: int,
    list_service: ListService = Depends(get_list_service),
    user_internal_id: int = Depends(get_current_user_id),
    _: None = Depends(require_list_creator)
):
    result = list_service.delete_list(list_id, user_internal_id)
    return ResponseModel(data=result, message="List deleted successfully")

@router.post("/{list_id}/users", response_model=ResponseModel[ListInDB])
async def add_user_to_list(
    list_id: int,
    user_data: ListAddUser,
    list_service: ListService = Depends(get_list_service),
    user_service: UserService = Depends(get_user_service),
    user_internal_id: int = Depends(get_current_user_id),
    _: None = Depends(require_list_creator)
):
    user_to_add = user_service.get_user_by_external_id(user_data.user_external_id)
    if not user_to_add:
        raise NotFoundException(f"User with external ID {user_data.user_external_id} not found")
    
    updated_list = list_service.add_user_to_list(list_id, user_to_add.id, user_internal_id)
    return ResponseModel(data=updated_list, message="User added to list successfully")

@router.delete("/{list_id}/users", response_model=ResponseModel[ListInDB])
async def remove_user_from_list(
    list_id: int,
    user_data: ListRemoveUser,
    list_service: ListService = Depends(get_list_service),
    user_service: UserService = Depends(get_user_service),
    user_internal_id: int = Depends(get_current_user_id),
    _: None = Depends(require_list_creator)
):
    user_to_remove = user_service.get_user_by_external_id(user_data.user_external_id)
    if not user_to_remove:
        raise NotFoundException(f"User with external ID {user_data.user_external_id} not found")
    updated_list = list_service.remove_user_from_list(list_id, user_to_remove.id, user_internal_id)
    return ResponseModel(data=updated_list, message="User removed from list successfully")

@router.post("/{list_id}/items", response_model=ResponseModel[ItemInDB])
async def create_item(
    list_id: int,
    item_create: ItemCreate,
    item_service: ItemService = Depends(get_item_service),
    user_internal_id: int = Depends(get_current_user_id),
    _: None = Depends(require_list_access)
):
    item = item_service.create_item(list_id, item_create, user_internal_id)
    return ResponseModel(data=item, message="Item created successfully")

@router.get("/{list_id}/items", response_model=ResponseModel[TypeList[ItemInDB]])
async def get_items(
    list_id: int,
    item_service: ItemService = Depends(get_item_service),
    user_internal_id: int = Depends(get_current_user_id),
    _: None = Depends(require_list_access)
):
    items = item_service.get_items_by_list_id(list_id, user_internal_id)
    return ResponseModel(data=items, message="Items retrieved successfully")

@router.put("/{list_id}/items/{item_id}", response_model=ResponseModel[ItemInDB])
async def update_item(
    list_id: int,
    item_id: int,
    item_update: ItemUpdate,
    item_service: ItemService = Depends(get_item_service),
    user_internal_id: int = Depends(get_current_user_id),
    _: None = Depends(require_list_access)
):
    item = item_service.update_item(list_id, item_id, item_update, user_internal_id)
    return ResponseModel(data=item, message="Item updated successfully")

@router.delete("/{list_id}/items/{item_id}", response_model=ResponseModel[Dict])
async def delete_item(
    list_id: int,
    item_id: int,
    item_service: ItemService = Depends(get_item_service),
    user_internal_id: int = Depends(get_current_user_id),
    _: None = Depends(require_list_access)
):
    item_service.delete_item(list_id, item_id, user_internal_id)
    return ResponseModel(data={"status": "success"}, message="Item deleted successfully")

@router.post("/{list_id}/lock", response_model=ResponseModel[StatusMessage])
async def acquire_lock(
    list_id: int,
    lock_service: LockService = Depends(get_lock_service),
    user_internal_id: int = Depends(get_current_user_id),
    _: None = Depends(require_list_access)
):
    lock = lock_service.acquire_lock(list_id, user_internal_id)
    return ResponseModel(data={"status": "success", "lock": lock}, message="Lock acquired successfully")

@router.delete("/{list_id}/lock", response_model=ResponseModel[StatusMessage])
async def release_lock(
    list_id: int,
    lock_service: LockService = Depends(get_lock_service),
    user_internal_id: int = Depends(get_current_user_id),
    _: None = Depends(require_list_access)
):
    result = lock_service.release_lock(list_id, user_internal_id)
    return ResponseModel(data=result, message="Lock released successfully")
