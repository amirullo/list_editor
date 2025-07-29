from fastapi import Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.db import get_db
from app.repositories.list_repository import ListRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.user_repository import UserRepository
from app.services.list_service import ListService
from app.services.item_service import ItemService
from app.models.role_model import RoleType
from app.core.exceptions import ForbiddenException

def get_user_id(x_user_id: Optional[str] = Header(None)) -> str:
    """
    Get user ID from header or generate a new one
    """
    if not x_user_id:
        return str(uuid.uuid4())
    return x_user_id

# Repository dependencies
def get_list_repository(db: Session = Depends(get_db)) -> ListRepository:
    return ListRepository(db)

def get_item_repository(db: Session = Depends(get_db)) -> ItemRepository:
    return ItemRepository(db)

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

# Service dependencies
def get_list_service(
    db: Session = Depends(get_db),
    list_repo: ListRepository = Depends(get_list_repository)
) -> ListService:
    return ListService(db, list_repo)

def get_item_service(
    db: Session = Depends(get_db),
    item_repo: ItemRepository = Depends(get_item_repository),
    list_repo: ListRepository = Depends(get_list_repository)
) -> ItemService:
    return ItemService(db, item_repo, list_repo)

# Optional services - add if they exist
try:
    from app.repositories.lock_repository import LockRepository
    from app.services.lock_service import LockService
    
    def get_lock_repository(db: Session = Depends(get_db)) -> LockRepository:
        return LockRepository(db)
    
    def get_lock_service(
        db: Session = Depends(get_db),
        lock_repo: LockRepository = Depends(get_lock_repository)
    ) -> LockService:
        return LockService(db, lock_repo)
except ImportError:
    def get_lock_service():
        return None

try:
    from app.repositories.role_repository import RoleRepository
    from app.services.role_service import RoleService
    
    def get_role_repository(db: Session = Depends(get_db)) -> RoleRepository:
        return RoleRepository(db)
    
    def get_role_service(
        db: Session = Depends(get_db)
    ) -> RoleService:
        return RoleService(db)
except ImportError:
    def get_role_service():
        return None

def get_user_role(
    user_id: str = Depends(get_user_id),
    role_service: Optional[RoleService] = Depends(get_role_service)
) -> RoleType:
    """Get user role for authorization"""
    if not role_service:
        return RoleType.CLIENT  # Default role if role service not available
    
    role = role_service.get_role(user_id)
    if not role:
        # Auto-assign CLIENT role if none exists (following README's client/worker pattern)
        role = role_service.create_role(user_id, RoleType.CLIENT)
    return role.role_type

def require_worker_role(role: RoleType = Depends(get_user_role)):
    """Dependency to ensure user has worker role"""
    if role != RoleType.WORKER:
        raise ForbiddenException("Worker role required")
