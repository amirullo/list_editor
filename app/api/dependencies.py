from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.global_role_model import GlobalRoleType
from app.models.list_role_model import ListRoleType
from app.services.global_role_service import GlobalRoleService
from app.services.list_role_service import ListRoleService
from app.services.item_service import ItemService
from app.services.lock_service import LockService
from app.repositories.global_role_repository import GlobalRoleRepository
from app.repositories.list_user_repository import ListUserRepository
from app.repositories.list_repository import ListRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.user_repository import UserRepository
from typing import Optional, Any


def get_external_user_id(user_external_id: str = Header(..., alias="X-User-ID")) -> str:
    if not user_external_id:
        raise HTTPException(status_code=401, detail="User ID header required")
    return user_external_id

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_current_user_id(
    user_external_id: str = Depends(get_external_user_id),
    user_repo: UserRepository = Depends(get_user_repository)
) -> int:
    user = user_repo.get_by_external_id(user_external_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found or not authorized")
    return user.id

def get_global_role_repository(db: Session = Depends(get_db)) -> GlobalRoleRepository:
    return GlobalRoleRepository(db)

def get_list_user_repository(db: Session = Depends(get_db)) -> ListUserRepository:
    return ListUserRepository(db)

def get_list_repository(db: Session = Depends(get_db)) -> ListRepository:
    return ListRepository(db)

def get_item_repository(db: Session = Depends(get_db)) -> ItemRepository:
    return ItemRepository(db)

def get_global_role_service(
    global_role_repo: GlobalRoleRepository = Depends(get_global_role_repository)
) -> GlobalRoleService:
    return GlobalRoleService(global_role_repo)

def get_list_role_service(
    list_user_repo: ListUserRepository = Depends(get_list_user_repository)
) -> ListRoleService:
    return ListRoleService(list_user_repo)

def get_lock_service(db: Session = Depends(get_db)) -> LockService:
    return LockService(db)

async def get_list_service(db: Session = Depends(get_db)) -> "ListService":
    from app.services.list_service import ListService
    return ListService(
        db=db,
        list_repository=get_list_repository(db),
        user_repository=get_user_repository(db),
        list_user_repository=get_list_user_repository(db),
        global_role_service=get_global_role_service(get_global_role_repository(db)),
        list_role_service=get_list_role_service(get_list_user_repository(db)),
        item_service=get_item_service(db, get_item_repository(db), get_list_repository(db), get_global_role_service(get_global_role_repository(db)), get_list_role_service(get_list_user_repository(db)))
    )

def get_item_service(
    db: Session = Depends(get_db),
    item_repo: ItemRepository = Depends(get_item_repository),
    list_repo: ListRepository = Depends(get_list_repository),
    global_role_service: GlobalRoleService = Depends(get_global_role_service),
    list_role_service: ListRoleService = Depends(get_list_role_service)
) -> ItemService:
    return ItemService(
        db=db,
        item_repository=item_repo,
        list_repository=list_repo,
        global_role_service=global_role_service,
        list_role_service=list_role_service
    )

def get_user_global_role(
    user_internal_id: int = Depends(get_current_user_id),
    global_role_service: GlobalRoleService = Depends(get_global_role_service)
) -> GlobalRoleType:
    role = global_role_service.get_role(user_internal_id)
    if not role:
        role = global_role_service.create_role(user_internal_id, GlobalRoleType.CLIENT)
    return role.role_type

def get_user_list_role(list_id: int):
    def _get_user_list_role(
        user_internal_id: int = Depends(get_current_user_id),
        list_role_service: ListRoleService = Depends(get_list_role_service)
    ) -> Optional[ListRoleType]:
        return list_role_service.get_user_role_in_list(user_internal_id, list_id)
    return _get_user_list_role

def require_global_role(required_role: GlobalRoleType):
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
    user_internal_id: int = Depends(get_current_user_id),
    list_role_service: ListRoleService = Depends(get_list_role_service)
) -> None:
    has_access = await list_role_service.user_has_access_to_list(user_internal_id, list_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied to this list")

async def require_list_creator(
    list_id: int,
    user_internal_id: int = Depends(get_current_user_id),
    list_role_service: ListRoleService = Depends(get_list_role_service)
) -> None:
    is_creator = await list_role_service.is_user_list_creator(user_internal_id, list_id)
    if not is_creator:
        raise HTTPException(status_code=403, detail="Only list creator can perform this action")
