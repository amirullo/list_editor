from fastapi import APIRouter, Depends, HTTPException, status
from typing import List as TypeList, Dict, Any, List
from app.schemas.list_schema import ListCreate, ListUpdate, ListInDB
from app.schemas.item_schema import ItemCreate, ItemUpdate, ItemInDB
from app.schemas.response_schema import Response, StatusMessage
from app.services.list_service import ListService
from app.services.item_service import ItemService
from app.services.lock_service import LockService
from app.api.dependencies import (
    get_list_service, get_item_service, get_lock_service,
    get_user_id, ensure_client_role, ensure_worker_role
)
from app.core.exceptions import NotFoundException, LockException
from app.utils.logger import logger

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
    list_id: int,
    list_service: ListService = Depends(get_list_service),
    user_id: str = Depends(get_user_id)
):
    """
    Get a specific list by ID
    """
    try:
        list_obj = list_service.get_list(list_id)
        return Response(
            status="success",
            message="List retrieved successfully",
            data=list_obj
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{list_id}", response_model=Response[ListInDB])
def update_list(
    list_id: int,
    list_update: ListUpdate,
    list_service: ListService = Depends(get_list_service),
    user_id: str = Depends(ensure_worker_role)
):
    """
    Update a list (requires worker role)
    """
    try:
        updated_list = list_service.update_list(list_id, user_id, list_update)
        return Response(
            status="success",
            message="List updated successfully",
            data=updated_list
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LockException as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/{list_id}", response_model=Response[StatusMessage])
def delete_list(
    list_id: int,
    list_service: ListService = Depends(get_list_service),
    user_id: str = Depends(ensure_worker_role)
):
    """
    Delete a list (requires worker role)
    """
    try:
        result = list_service.delete_list(list_id, user_id)
        return Response(
            status="success",
            message="List deleted successfully",
            data={"message": "List deleted successfully"}
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LockException as e:
        raise HTTPException(status_code=409, detail=str(e))

# Item endpoints
@router.post("/{list_id}/items", response_model=Response[ItemInDB])
def create_item(
    list_id: int,
    item_create: ItemCreate,
    item_service: ItemService = Depends(get_item_service),
    user_id: str = Depends(ensure_worker_role)
):
    """
    Add an item to a specific list (requires worker role)
    """
    try:
        item = item_service.create_item(list_id, item_create)
        return Response(
            status="success",
            message="Item added successfully",
            data=item
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LockException as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.put("/{list_id}/items/{item_id}", response_model=Response[ItemInDB])
def update_item(
    list_id: int,
    item_id: int,
    item_update: ItemUpdate,
    # list_update: ListUpdate,
    item_service: ItemService = Depends(get_item_service),
    user_id: str = Depends(ensure_worker_role)
):
    """
    Update an item in a specific list (requires worker role)
    """
    try:
        updated_item = item_service.update_item(list_id, item_id, item_update, user_id)
        return Response(
            status="success",
            message="Item updated successfully",
            data=updated_item
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LockException as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/{list_id}/items/{item_id}", response_model=Response[Dict])
def delete_item(
    list_id: int,
    item_id: int,
    item_service: ItemService = Depends(get_item_service),
    user_id: str = Depends(ensure_worker_role)
):
    """
    Delete an item from a specific list (requires worker role)
    """
    try:
        item_service.delete_item(list_id, item_id)
        return Response(
            status="success",
            message="Item deleted successfully",
            data={"id": item_id}
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LockException as e:
        raise HTTPException(status_code=409, detail=str(e))

# Lock endpoints
@router.post("/{list_id}/lock", response_model=Response[StatusMessage])
def acquire_lock(
    list_id: int,
    lock_service: LockService = Depends(get_lock_service),
    user_id: str = Depends(ensure_worker_role)
):
    """
    Acquire a lock on a list (requires worker role)
    """
    try:
        lock = lock_service.acquire_lock(list_id, user_id)
        return Response(
            status="success",
            message="Lock acquired successfully",
            data={"message": "Lock acquired successfully"}
        )
    except LockException as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.delete("/{list_id}/lock", response_model=Response[StatusMessage])
def release_lock(
    list_id: int,
    lock_service: LockService = Depends(get_lock_service),
    user_id: str = Depends(ensure_worker_role)
):
    """
    Release a lock on a list (requires worker role)
    """
    try:
        result = lock_service.release_lock(list_id, user_id)
        return Response(
            status="success",
            message="Lock released successfully",
            data={"message": "Lock released successfully"}
        )
    except LockException as e:
        raise HTTPException(status_code=409, detail=str(e))