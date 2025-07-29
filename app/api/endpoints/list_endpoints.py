from fastapi import APIRouter, Depends, HTTPException, status
from typing import List as TypeList, Dict, Any, List
from app.schemas.list_schema import ListCreate, ListUpdate, ListInDB, ListAddUser, ListRemoveUser
from app.schemas.item_schema import ItemCreate, ItemUpdate, ItemInDB
from app.schemas.response_schema import ResponseModel, StatusMessage
from app.services.list_service import ListService
from app.services.item_service import ItemService
from app.services.lock_service import LockService
from app.api.dependencies import (
    get_list_service, get_item_service, get_lock_service,
    get_user_id
)
from app.core.exceptions import NotFoundException, LockException, ForbiddenException
from app.utils.logger import logger

router = APIRouter()

# List endpoints
@router.post("/", response_model=ResponseModel[ListInDB])
def create_list(
    list_create: ListCreate,
    items: TypeList[ItemCreate] = None,
    list_service: ListService = Depends(get_list_service),
    user_id: str = Depends(get_user_id)  # Any authenticated user can create
):
    """Create a new list with the current user as creator"""
    try:
        list_data = list_service.create_list(list_create, user_id, items)
        return ResponseModel(
            status="success",
            message="List created successfully",
            data=list_data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=ResponseModel[TypeList[ListInDB]])
def get_all_lists(
    list_service: ListService = Depends(get_list_service),
    user_id: str = Depends(get_user_id)
):
    """Get all lists accessible to the user"""
    try:
        lists = list_service.get_all_lists(user_id)
        return ResponseModel(
            status="success",
            message="Lists retrieved successfully",
            data=lists
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{list_id}", response_model=ResponseModel[ListInDB])
def get_list(
    list_id: int,
    list_service: ListService = Depends(get_list_service),
    user_id: str = Depends(get_user_id)
):
    """Get list details - accessible to participants only"""
    try:
        list_data = list_service.get_list(list_id, user_id)
        return ResponseModel(
            status="success",
            message="List retrieved successfully",
            data=list_data
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.put("/{list_id}", response_model=ResponseModel[ListInDB])
def update_list(
    list_id: int,
    list_update: ListUpdate,
    list_service: ListService = Depends(get_list_service),
    user_id: str = Depends(get_user_id)  # ✅ FIXED: All participants can update
):
    """Update list - accessible to all participants"""
    try:
        updated_list = list_service.update_list(list_id, list_update, user_id)
        return ResponseModel(
            status="success",
            message="List updated successfully",
            data=updated_list
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except LockException as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/{list_id}", response_model=ResponseModel[StatusMessage])
def delete_list(
    list_id: int,
    list_service: ListService = Depends(get_list_service),
    user_id: str = Depends(get_user_id)  # ✅ FIXED: Only creator check is in service
):
    """Delete list - only creator can delete"""
    try:
        result = list_service.delete_list(list_id, user_id)
        return ResponseModel(
            status="success",
            message="List deleted successfully",
            data={"message": "List deleted successfully"}
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=403, detail=str(e))

# User management endpoints
@router.post("/{list_id}/users", response_model=ResponseModel[ListInDB])
def add_user_to_list(
    list_id: int,
    user_data: ListAddUser,
    list_service: ListService = Depends(get_list_service),
    user_id: str = Depends(get_user_id)
):
    """Add user to list - only creator can add users"""
    try:
        updated_list = list_service.add_user_to_list(list_id, user_data.user_id, user_id)
        return ResponseModel(
            status="success",
            message="User added to list successfully",
            data=updated_list
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/{list_id}/users/{user_id_to_remove}", response_model=ResponseModel[ListInDB])
def remove_user_from_list(
    list_id: int,
    user_id_to_remove: str,
    list_service: ListService = Depends(get_list_service),
    user_id: str = Depends(get_user_id)
):
    """Remove user from list - only creator can remove users"""
    try:
        updated_list = list_service.remove_user_from_list(list_id, user_id_to_remove, user_id)
        return ResponseModel(
            status="success",
            message="User removed from list successfully",
            data=updated_list
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenException as e:
        raise HTTPException(status_code=403, detail=str(e))

# Item endpoints - ALL PARTICIPANTS CAN MODIFY
@router.post("/{list_id}/items", response_model=ResponseModel[ItemInDB])
def create_item(
    list_id: int,
    item_create: ItemCreate,
    item_service: ItemService = Depends(get_item_service),
    user_id: str = Depends(get_user_id)  # ✅ FIXED: All participants
):
    """Create item - accessible to all list participants"""
    try:
        item = item_service.create_item(list_id, item_create, user_id)
        return ResponseModel(
            status="success",
            message="Item created successfully",
            data=item
        )
    except ForbiddenException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LockException as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.put("/{list_id}/items/{item_id}", response_model=ResponseModel[ItemInDB])
def update_item(
    list_id: int,
    item_id: int,
    item_update: ItemUpdate,
    item_service: ItemService = Depends(get_item_service),
    user_id: str = Depends(get_user_id)  # ✅ FIXED: All participants
):
    """Update item - accessible to all list participants"""
    try:
        item = item_service.update_item(list_id, item_id, item_update, user_id)
        return ResponseModel(
            status="success",
            message="Item updated successfully",
            data=item
        )
    except ForbiddenException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LockException as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/{list_id}/items/{item_id}", response_model=ResponseModel[Dict])
def delete_item(
    list_id: int,
    item_id: int,
    item_service: ItemService = Depends(get_item_service),
    user_id: str = Depends(get_user_id)  # ✅ FIXED: All participants
):
    """Delete item - accessible to all list participants"""
    try:
        result = item_service.delete_item(list_id, item_id, user_id)
        return ResponseModel(
            status="success",
            message="Item deleted successfully",
            data=result
        )
    except ForbiddenException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LockException as e:
        raise HTTPException(status_code=409, detail=str(e))

# Lock endpoints - ALL PARTICIPANTS CAN LOCK
@router.post("/{list_id}/lock", response_model=ResponseModel[StatusMessage])
def acquire_lock(
    list_id: int,
    lock_service: LockService = Depends(get_lock_service),
    user_id: str = Depends(get_user_id)  # ✅ FIXED: All participants
):
    """Acquire lock - accessible to all list participants"""
    try:
        result = lock_service.acquire_lock(list_id, user_id)
        return ResponseModel(
            status="success",
            message="Lock acquired successfully",
            data={"message": "Lock acquired successfully"}
        )
    except ForbiddenException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except LockException as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/{list_id}/lock", response_model=ResponseModel[StatusMessage])
def release_lock(
    list_id: int,
    lock_service: LockService = Depends(get_lock_service),
    user_id: str = Depends(get_user_id)  # ✅ FIXED: All participants
):
    """Release lock - accessible to all list participants"""
    try:
        result = lock_service.release_lock(list_id, user_id)
        return ResponseModel(
            status="success",
            message="Lock released successfully",
            data={"message": "Lock released successfully"}
        )
    except ForbiddenException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except LockException as e:
        raise HTTPException(status_code=409, detail=str(e))