from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.models.global_role_model import GlobalRoleType
from app.models.list_role_model import ListRoleType
from app.services.global_role_service import GlobalRoleService
from app.services.list_role_service import ListRoleService
# from app.services.list_service import ListService
from app.services.item_service import ItemService
from app.services.lock_service import LockService
from app.repositories.global_role_repository import GlobalRoleRepository
from app.repositories.list_user_repository import ListUserRepository
from app.repositories.list_repository import ListRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.user_repository import UserRepository
from typing import Optional, Coroutine, Any

def get_user_id(x_user_id: str = Header(..., alias="X-User-ID")) -> str:
    """Get user ID from request headers"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID header required")
    return x_user_id

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_current_user_id(
    external_user_id: str = Depends(get_user_id),
    user_repo: UserRepository = Depends(get_user_repository)
) -> int:
    """
    Gets the external user_id from the header, finds the user in the DB,
    and returns their internal integer ID.
    """
    user = user_repo.get_by_id(external_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found or not authorized")
    return user.id

def get_global_role_repository(db: Session = Depends(get_db)) -> GlobalRoleRepository:
    """Dependency to get global role repository"""
    return GlobalRoleRepository(db)

def get_list_user_repository(db: Session = Depends(get_db)) -> ListUserRepository:
    """Dependency to get list user repository"""
    return ListUserRepository(db)

def get_list_repository(db: Session = Depends(get_db)) -> ListRepository:
    """Dependency to get list repository"""
    return ListRepository(db)

def get_item_repository(db: Session = Depends(get_db)) -> ItemRepository:
    """Dependency to get item repository"""
    return ItemRepository(db)

def get_global_role_service(
    global_role_repo: GlobalRoleRepository = Depends(get_global_role_repository)
) -> GlobalRoleService:
    """Dependency to get global role service"""
    return GlobalRoleService(global_role_repo)

def get_list_role_service(
    list_user_repo: ListUserRepository = Depends(get_list_user_repository)
) -> ListRoleService:
    """Dependency to get list role service"""
    return ListRoleService(list_user_repo)

def get_lock_service(db: Session = Depends(get_db)) -> LockService:
    """Dependency to get lock service"""
    return LockService(db)

async def get_list_service(db: Session = Depends(get_db)) -> "ListService":
    # Import only what we know exists and works
    from app.repositories.list_repository import ListRepository
    from app.repositories.user_repository import UserRepository
    from app.repositories.list_user_repository import ListUserRepository
    from app.services.list_service import ListService
    
    # Create repositories
    list_repository = ListRepository(db)
    user_repository = UserRepository(db)
    list_user_repository = ListUserRepository(db)
    
    # Get the services that already work
    global_role_service = get_global_role_service(db)
    list_role_service = get_list_role_service(db)
    item_service = get_item_service(db)
    
    # Create ListService with all required arguments

    return ListService(
        list_repository=list_repository,
        db=db,
        list_user_repository=list_user_repository,
        user_repository=user_repository,
        global_role_service=global_role_service,
        list_role_service=list_role_service,
        item_service=item_service
    )

def get_item_service(
    item_repo: ItemRepository = Depends(get_item_repository),
    list_repo: ListRepository = Depends(get_list_repository),
    global_role_service: GlobalRoleService = Depends(get_global_role_service),
    list_role_service: ListRoleService = Depends(get_list_role_service)
) -> ItemService:
    """Dependency to get item service"""
    return ItemService(
        item_repository=item_repo,
        list_repository=list_repo,
        global_role_service=global_role_service,
        list_role_service=list_role_service
    )

def get_user_global_role(
    user_id: str = Depends(get_user_id),
    global_role_service: GlobalRoleService = Depends(get_global_role_service)
) -> GlobalRoleType:
    """Get user global role for authorization"""
    role = global_role_service.get_role(user_id)
    if not role:
        # Auto-assign CLIENT role if none exists
        role = global_role_service.create_role(user_id, GlobalRoleType.CLIENT)
    return role.role_type

def get_user_list_role(list_id: int):
    """Factory function to create list role dependency for specific list"""
    def _get_user_list_role(
        user_id: str = Depends(get_user_id),
        list_role_service: ListRoleService = Depends(get_list_role_service)
    ) -> Optional[ListRoleType]:
        return list_role_service.get_user_role_in_list(user_id, list_id)
    return _get_user_list_role

def require_global_role(required_role: GlobalRoleType):
    """Factory function to create role requirement dependency"""
    def _require_role(
        user_role: GlobalRoleType = Depends(get_user_global_role)
    ) -> GlobalRoleType:
        if user_role != required_role:
            raise HTTPException(
                status_code=403, 
                detail=f"Required role: {required_role.value}, current role: {user_role.value}"
            )
        return user_role
    return _require_role

async def require_list_access(
    list_id: int,
    user_id: str = Depends(get_user_id),
    list_role_service: ListRoleService = Depends(get_list_role_service)
) -> None:
    """Dependency to ensure the user has access to the list."""
    has_access = await list_role_service.user_has_access_to_list(user_id, list_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied to this list")

async def require_list_creator(
    list_id: int,
    user_id: str = Depends(get_user_id),
    list_role_service: ListRoleService = Depends(get_list_role_service)
) -> None:
    """Dependency to ensure the user is the creator of the list."""
    is_creator = await list_role_service.is_user_list_creator(user_id, list_id)
    if not is_creator:
        raise HTTPException(status_code=403, detail="Only list creator can perform this action")
