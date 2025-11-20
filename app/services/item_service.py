from typing import Optional, Dict, Any, List as TypeList
from sqlalchemy.orm import Session
from app.repositories.item_repository import ItemRepository
from app.repositories.list_repository import ListRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.item_schema import ItemCreate, ItemUpdate, ItemInDB
from app.core.exceptions import NotFoundException, LockException, ForbiddenException
from app.services.notification_service import NotificationService
from app.services.global_role_service import GlobalRoleService
from app.models.global_role_model import GlobalRoleType
from app.utils.logger import logger
from uuid import UUID # Import UUID

class ItemService:
    def __init__(self, 
                 db: Session,
                 item_repository: ItemRepository,
                 list_repository: ListRepository,
                 project_repository: ProjectRepository,
                 global_role_service: GlobalRoleService):
        self.db = db
        self.item_repository = item_repository
        self.list_repository = list_repository
        self.project_repository = project_repository
        self.notification_service = NotificationService()
        self.global_role_service = global_role_service

    def _check_project_access(self, list_id: int, user_internal_id: UUID):
        db_list = self.list_repository.get_by_id(list_id)
        if not db_list:
            raise NotFoundException("List not found")
        
        project = self.project_repository.get_by_id_for_user(db_list.project_id, user_internal_id)
        if not project:
            raise ForbiddenException("You don't have access to this project")
        
        return db_list

    def _check_lock(self, list_id: int, user_internal_id: UUID):
        from app.services.lock_service import LockService
        lock_service = LockService(self.db)
        if not lock_service.check_lock(list_id, user_internal_id):
            raise LockException("List is locked by another user")

    def get_items_by_list(self, list_id: int, user_internal_id: UUID) -> TypeList[ItemInDB]:
        self._check_project_access(list_id, user_internal_id)
        
        items = self.item_repository.get_all_by_list(list_id)
        return [ItemInDB.model_validate(item) for item in items]
    
    def create_item(self, list_id: int, item_create: ItemCreate, user_internal_id: UUID) -> ItemInDB:
        self._check_project_access(list_id, user_internal_id)
        
        item_data = item_create.model_dump(exclude_unset=True)
        new_item = self.item_repository.create(list_id, item_data)
        
        logger.info(f"Created item {new_item.id} in list {list_id} by user {user_internal_id}")
        return ItemInDB.model_validate(new_item)

    def get_item(self, list_id: int, item_id: int, user_internal_id: UUID) -> ItemInDB:
        self._check_project_access(list_id, user_internal_id)
        
        item = self.item_repository.get_by_id(list_id, item_id)
        if not item:
            raise NotFoundException("Item not found")
        
        return ItemInDB.model_validate(item)

    def get_all_items(self, list_id: int, user_internal_id: UUID) -> TypeList[ItemInDB]:
        self._check_project_access(list_id, user_internal_id)
        
        items = self.item_repository.get_all_by_list(list_id)
        return [ItemInDB.model_validate(item) for item in items]

    def update_item(self, list_id: int, item_id: int, item_update: ItemUpdate, user_internal_id: UUID) -> ItemInDB:
        self._check_project_access(list_id, user_internal_id)
        
        current_item = self.item_repository.get_by_id(list_id, item_id)
        if not current_item:
            raise NotFoundException("Item not found")
        
        update_data = item_update.model_dump(exclude_unset=True)
        logger.info(f"update_item: user_internal_id={user_internal_id}, item_id={item_id}, update_data={update_data}")

        user_global_role = self.global_role_service.get_role(user_internal_id)
        if user_global_role:
            logger.info(f"update_item: User {user_internal_id} has global role {user_global_role.role_type.value}")
            if user_global_role.role_type == GlobalRoleType.CLIENT:
                for field in update_data:
                    if field != "price":
                        logger.warning(f"update_item: Client {user_internal_id} attempted to update non-price field: {field}")
                        raise ForbiddenException("Clients can only update item prices.")
            elif user_global_role.role_type == GlobalRoleType.WORKER:
                for field in update_data:
                    if field not in ["quantity", "approved", "bought", "delivered"]:
                        logger.warning(f"update_item: Worker {user_internal_id} attempted to update forbidden field: {field}")
                        raise ForbiddenException("Workers can only update item quantity and status fields (approved, bought, delivered).")
        else:
            logger.info(f"update_item: User {user_internal_id} has no global role assigned.")
        
        updated_item = self.item_repository.update(item_id, update_data)
        if not updated_item:
            raise NotFoundException("Item not found")
        
        logger.info(f"Updated item {item_id} in list {list_id} by user {user_internal_id}")
        return ItemInDB.model_validate(updated_item)

    def delete_item(self, list_id: int, item_id: int, user_internal_id: UUID) -> Dict[str, str]:
        self._check_project_access(list_id, user_internal_id)
        success = self.item_repository.delete(list_id, item_id)
        if not success:
            raise NotFoundException("Item not found")

        logger.info(f"Deleted item {item_id} from list {list_id} by user {user_internal_id}")
        return {"message": "Item deleted successfully"}
