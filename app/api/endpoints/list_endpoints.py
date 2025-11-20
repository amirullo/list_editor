
from fastapi import APIRouter, Depends, status
from typing import List as TypeList, Dict, Any, Optional
from app.schemas.list_schema import ListCreate, ListUpdate, ListInDB
from app.schemas.item_schema import ItemCreate, ItemUpdate, ItemInDB
from app.schemas.response_schema import ResponseModel
from app.schemas.lock_schema import LockInDB
from app.services.list_service import ListService
from app.services.item_service import ItemService
from app.services.lock_service import LockService
from app.api.dependencies import (
    get_list_service,
    get_item_service,
    get_lock_service,
    get_current_user_id,
    require_project_access,
)
from pydantic import BaseModel
from app.utils.logger import logger

class CreateListRequest(BaseModel):
    list_create: ListCreate
    items: Optional[TypeList[ItemCreate]] = None

router = APIRouter()

@router.post("/", response_model=ResponseModel[ListInDB], status_code=status.HTTP_201_CREATED)
async def create_list(
    request: CreateListRequest,
    list_service: ListService = Depends(get_list_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    new_list = list_service.create_list(request.list_create,
                                        user_internal_id,
                                        request.items)
    return ResponseModel(data=new_list, message="List created successfully")

@router.get("/project/{project_id}", response_model=ResponseModel[TypeList[ListInDB]])
def get_all_lists_for_project(
    project_id: int,
    list_service: ListService = Depends(get_list_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    lists = list_service.get_all_lists_for_project(project_id, user_internal_id)
    return ResponseModel(data=lists, message="Lists for project retrieved successfully")

@router.get("/{list_id}", response_model=ResponseModel[ListInDB])
async def get_list(
    list_id: int,
    list_service: ListService = Depends(get_list_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    db_list = list_service.get_list(list_id, user_internal_id)
    return ResponseModel(data=db_list, message="List retrieved successfully")

@router.put("/{list_id}", response_model=ResponseModel[ListInDB])
async def update_list(
    list_id: int,
    list_update: ListUpdate,
    list_service: ListService = Depends(get_list_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    updated_list = list_service.update_list(list_id, list_update, user_internal_id)
    return ResponseModel(data=updated_list, message="List updated successfully")

@router.delete("/{list_id}", response_model=ResponseModel[dict])
async def delete_list(
    list_id: int,
    list_service: ListService = Depends(get_list_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    result = list_service.delete_list(list_id, user_internal_id)
    return ResponseModel(data=result, message="List deleted successfully")

@router.post("/{list_id}/items", response_model=ResponseModel[ItemInDB])
async def create_item(
    list_id: int,
    item_create: ItemCreate,
    item_service: ItemService = Depends(get_item_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    item = item_service.create_item(list_id, item_create, user_internal_id)
    return ResponseModel(data=item, message="Item created successfully")

@router.get("/{list_id}/items", response_model=ResponseModel[TypeList[ItemInDB]])
async def get_items(
    list_id: int,
    item_service: ItemService = Depends(get_item_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    items = item_service.get_items_by_list(list_id, user_internal_id)
    return ResponseModel(data=items, message="Items retrieved successfully")

@router.put("/{list_id}/items/{item_id}", response_model=ResponseModel[ItemInDB])
async def update_item(
    list_id: int,
    item_id: int,
    item_update: ItemUpdate,
    item_service: ItemService = Depends(get_item_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    item = item_service.update_item(list_id, item_id, item_update, user_internal_id)
    return ResponseModel(data=item, message="Item updated successfully")

@router.delete("/{list_id}/items/{item_id}", response_model=ResponseModel[Dict])
async def delete_item(
    list_id: int,
    item_id: int,
    item_service: ItemService = Depends(get_item_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    item_service.delete_item(list_id, item_id, user_internal_id)
    return ResponseModel(data={"status": "success"}, message="Item deleted successfully")

@router.post("/{list_id}/lock", response_model=ResponseModel[LockInDB])
async def acquire_lock(
    list_id: int,
    lock_service: LockService = Depends(get_lock_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    lock = lock_service.acquire_lock(list_id, user_internal_id)
    return ResponseModel(data=LockInDB.model_validate(lock), message="Lock acquired successfully")

@router.delete("/{list_id}/lock", response_model=ResponseModel[None])
async def release_lock(
    list_id: int,
    lock_service: LockService = Depends(get_lock_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    result = lock_service.release_lock(list_id, user_internal_id)
    return ResponseModel(message="Lock released successfully")
