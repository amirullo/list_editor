
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.global_role_model import GlobalRoleType
from app.models.project_user_model import ProjectRoleType
from app.services.global_role_service import GlobalRoleService
from app.services.item_service import ItemService
from app.services.lock_service import LockService
from app.services.user_service import UserService
from app.services.project_service import ProjectService
from app.repositories.global_role_repository import GlobalRoleRepository
from app.repositories.project_user_repository import ProjectUserRepository
from app.repositories.list_repository import ListRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.user_repository import UserRepository
from app.repositories.project_repository import ProjectRepository
from typing import Optional
from app.utils.logger import logger # Import logger

def get_external_user_id(user_external_id: str = Header(..., alias="X-User-ID")) -> str:
    if not user_external_id:
        raise HTTPException(status_code=401, detail="User ID header required")
    return user_external_id

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_user_service(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repo)

def get_current_user_id(
    user_external_id: str = Depends(get_external_user_id),
    user_service: UserService = Depends(get_user_service)
) -> int: # Changed return type to int
    user = user_service.get_or_create_user_by_external_id(user_external_id) # Use get_or_create
    if not user:
        raise HTTPException(status_code=401, detail="User not found or not authorized")
    logger.info(f"get_current_user_id: Returning internal_id {user.internal_id} for external_user_id {user_external_id}")
    return user.internal_id # Return internal_id

def get_global_role_repository(db: Session = Depends(get_db)) -> GlobalRoleRepository:
    return GlobalRoleRepository(db)

def get_project_user_repository(db: Session = Depends(get_db)) -> ProjectUserRepository:
    return ProjectUserRepository(db)

def get_list_repository(db: Session = Depends(get_db)) -> ListRepository:
    return ListRepository(db)

def get_item_repository(db: Session = Depends(get_db)) -> ItemRepository:
    return ItemRepository(db)

def get_project_repository(db: Session = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(db)

def get_global_role_service(
    global_role_repo: GlobalRoleRepository = Depends(get_global_role_repository)
) -> GlobalRoleService:
    return GlobalRoleService(global_role_repo)

def get_project_service(
    db: Session = Depends(get_db)
) -> ProjectService:
    return ProjectService(db)

def get_lock_service(db: Session = Depends(get_db)) -> LockService:
    return LockService(db)

def get_item_service(
    db: Session = Depends(get_db),
    item_repo: ItemRepository = Depends(get_item_repository),
    list_repo: ListRepository = Depends(get_list_repository),
    project_repo: ProjectRepository = Depends(get_project_repository), # Add project_repo dependency
    global_role_service: GlobalRoleService = Depends(get_global_role_service) # Inject GlobalRoleService
) -> ItemService:
    return ItemService(
        db=db,
        item_repository=item_repo,
        list_repository=list_repo,
        project_repository=project_repo, # Pass project_repository
        global_role_service=global_role_service # Pass GlobalRoleService
    )

def get_list_service(
    db: Session = Depends(get_db),
    list_repo: ListRepository = Depends(get_list_repository),
    project_repo: ProjectRepository = Depends(get_project_repository),
    item_service: ItemService = Depends(get_item_service)
) -> "ListService":
    from app.services.list_service import ListService
    return ListService(
        db=db,
        list_repository=list_repo,
        project_repository=project_repo,
        item_service=item_service
    )

def get_user_global_role(
    user_internal_id: int = Depends(get_current_user_id), # Changed type to int
    global_role_service: GlobalRoleService = Depends(get_global_role_service)
) -> GlobalRoleType:
    role = global_role_service.get_role(user_internal_id)
    if not role:
        role = global_role_service.create_role(user_internal_id, GlobalRoleType.CLIENT)
    return role.role_type

def require_project_access(
    project_id: int,
    user_internal_id: int = Depends(get_current_user_id), # Changed type to int
    project_repo: ProjectRepository = Depends(get_project_repository)
) -> None:
    project = project_repo.get_by_id_for_user(project_id, user_internal_id)
    if not project:
        raise HTTPException(status_code=403, detail="Access denied to this project")
