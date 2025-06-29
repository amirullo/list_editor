from fastapi import APIRouter, Depends
from typing import List as TypeList

from app.services.notification_service import NotificationService
from app.api.dependencies import get_user_id

router = APIRouter()

@router.get("/notifications", response_model=TypeList[str])
def get_notifications(
    notification_service: NotificationService = Depends(),
    user_id: str = Depends(get_user_id)
):
    """
    Get all notifications for the user
    """
    return notification_service.get_notifications()