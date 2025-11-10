from fastapi import APIRouter, Depends
from typing import List as TypeList

from app.services.notification_service import NotificationService
from app.api.dependencies import get_current_user_id, get_list_service
from app.services.list_service import ListService
from app.schemas.response_schema import ResponseModel
from app.schemas.list_schema import ListInDB

router = APIRouter()

@router.get("/notifications", response_model=TypeList[str])
def get_notifications(
    notification_service: NotificationService = Depends(),
    user_internal_id: int = Depends(get_current_user_id)
):
    """
    Get notifications for changes
    """
    return notification_service.get_notifications()

@router.post("/lists/{list_id}/sync", response_model=ResponseModel[ListInDB])
def sync_list(
    list_id: int, 
    user_internal_id: int = Depends(get_current_user_id),
    list_service: ListService = Depends(get_list_service)
):
    """Manual synchronization endpoint as mentioned in README"""
    # Get the latest version of the list
    updated_list = list_service.get_list(list_id, user_internal_id)
    return ResponseModel(
        success=True,
        message="List synchronized successfully",
        data=updated_list
    )