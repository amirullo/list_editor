from fastapi import APIRouter, Depends, HTTPException, status
from typing import List as TypeList, Dict, Any

from app.schemas.list_schema import (
    ListCreate, ListUpdate, ListInDB,
    ItemCreate, ItemUpdate, ItemInDB
)
from app.schemas.response_schema import Response, StatusMessage
from app.services.list_service import ListService
from app.services.item_service import ItemService
from app.services.lock_service import LockService
from app.api.dependencies import (
    get_list_service, get_item_service, get_lock_service,
    get_user_id, ensure_client_role, ensure_worker_role
)

router = APIRouter()

# List endpoints
@router.post("/", response_model=Response[ListInDB])
def create_list(
    list_create: ListCreate,
    items: TypeList[ItemCreate] = None,
    list_service: ListService = Depends(get_list_service),
    user_id: str = Depends(ensure_client_role)
):
    """
    Create a new list with optional items
    """
    list_obj = list_service.create_list(list_create, items)
    return Response(
        status="success",
        message="List created successfully",
        data=list_obj
    )

@router.get("/", response_model=Response[TypeList[ListInDB]])
def get_all_lists(
    list_service: ListService = Depends(get_list_service),
    user_id: str = Depends(get_user_id)
):
    """
    Get all lists
    """
    lists = list_service.get_all_lists()
    return Response(
        status="success",
        message="Lists retrieved successfully",
        data=lists
    )

@router.get("/{list_id}", response_model=Response[ListInDB])
def get_list(
    list_id: str,
    list_service: ListService = Depends(get_list_service),
    user_id: str = Depends(get_user_id)
):
    """
    Get a specific list by ID
    """
    list_obj = list_service.get_list(list_id)
    return Response(
        status="success",
        message="List retrieved successfully",
        data=list_obj
    )

@router.put("/{list_id}", response_model=Response[ListInDB])
def update_list(
    list_id: str,
    list_update: ListUpdate,
    list_service: ListService = Depends(get_list_service),
    user_id: str = Depends(ensure_worker_role)
):
    """
    Update a list (requires worker role)
    """
    updated_list = list_service.update_list(list_id, user_id, list_update)
    return Response(
        status="success",
        message="List updated successfully",
        data=updated_list
    )

@router.delete("/{list_id}", response_model=Response[StatusMessage])
def delete_list(
    list_id: str,
    list_service: ListService = Depends(get_list_service),
    user_id: str = Depends(ensure_worker_role)
):
    """
    Delete a list (requires worker role)
    """
    result = list_service.delete_list(list_id, user_id)
    return Response(
        status="success",
        message="List deleted successfully",
        data={"message": "List deleted successfully"}
    )

# Item endpoints
@router.post("/{list_id}/items", response_model=Response[ItemInDB])
def create_item(
    list_id: str,
    item_create: ItemCreate,
    item_service: ItemService = Depends(get_item_service),
    user_id: str = Depends(ensure_worker_role)
):
    """
    Add an item to a list (requires worker role)
    """
    item = item_service.create_item(list_id, user_id, item_create)
    return Response(
        status="success",
        message="Item added successfully",
        data=item
    )

@router.put("/items/{item_id}", response_model=Response[ItemInDB])
def update_item(
    item_id: str,
    item_update: ItemUpdate,
    item_service: ItemService = Depends(get_item_service),
    user_id: str = Depends(ensure_worker_role)
):
    """
    Update an item (requires worker role)
    """
    updated_item = item_service.update_item(item_id, user_id, item_update)
    return Response(
        status="success",
        message="Item updated successfully",
        data=updated_item
    )

@router.delete("/items/{item_id}", response_model=Response[StatusMessage])
def delete_item(
    item_id: str,
    item_service: ItemService = Depends(get_item_service),
    user_id: str = Depends(ensure_worker_role)
):
    """
    Delete an item (requires worker role)
    """
    result = item_service.delete_item(item_id, user_id)
    return Response(
        status="success",
        message="Item deleted successfully",
        data={"message": "Item deleted successfully"}
    )

# Lock endpoints
@router.post("/{list_id}/lock", response_model=Response[StatusMessage])
def acquire_lock(
    list_id: str,
    lock_service: LockService = Depends(get_lock_service),
    user_id: str = Depends(ensure_worker_role)
):
    """
    Acquire a lock on a list (requires worker role)
    """
    lock = lock_service.acquire_lock(list_id, user_id)
    return Response(
        status="success",
        message="Lock acquired successfully",
        data={"message": "Lock acquired successfully"}
    )

@router.delete("/{list_id}/lock", response_model=Response[StatusMessage])
def release_lock(
    list_id: str,
    lock_service: LockService = Depends(get_lock_service),
    user_id: str = Depends(ensure_worker_role)
):
    """
    Release a lock on a list (requires worker role)
    """
    result = lock_service.release_lock(list_id, user_id)
    return Response(
        status="success",
        message="Lock released successfully",
        data={"message": "Lock released successfully"}
    )