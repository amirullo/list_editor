from fastapi import Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.db import get_db
from app.services.list_service import ListService
from app.services.item_service import ItemService
from app.services.lock_service import LockService
from app.services.role_service import RoleService
from app.models.role_model import RoleType

def get_list_service(db: Session = Depends(get_db)) -> ListService:
    return ListService(db)

def get_item_service(db: Session = Depends(get_db)) -> ItemService:
    return ItemService(db)

def get_lock_service(db: Session = Depends(get_db)) -> LockService:
    return LockService(db)

def get_role_service(db: Session = Depends(get_db)) -> RoleService:
    return RoleService(db)

def get_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    """
    Get user ID from header or generate a new one
    """
    if not x_user_id:
        return str(uuid.uuid4())
    return x_user_id

def ensure_client_role(
    user_id: str = Depends(get_user_id),
    role_service: RoleService = Depends(get_role_service)
) -> str:
    """
    Ensure the user has client role
    """
    role_service.ensure_permission(user_id, RoleType.CLIENT)
    return user_id

def ensure_worker_role(
    user_id: str = Depends(get_user_id),
    role_service: RoleService = Depends(get_role_service)
) -> str:
    """
    Ensure the user has worker role
    """
    role_service.ensure_permission(user_id, RoleType.WORKER)
    return user_id