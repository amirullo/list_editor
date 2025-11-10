from typing import Optional, Dict, Any, List as TypeList
from sqlalchemy.orm import Session
from app.repositories.item_repository import ItemRepository
from app.repositories.list_repository import ListRepository
from app.schemas.item_schema import ItemCreate, ItemUpdate, ItemInDB
from app.models.list_role_model import ListRoleType
from app.models.global_role_model import GlobalRoleType
from app.core.exceptions import NotFoundException, LockException, ForbiddenException
from app.services.notification_service import NotificationService
from app.utils.logger import logger

class ItemService:
    def __init__(self, 
                 db: Session,
                 item_repository: ItemRepository,
                 list_repository: ListRepository,
                 global_role_service: Any,
                 list_role_service: Any):
        self.db = db
        self.item_repository = item_repository
        self.list_repository = list_repository
        self.global_role_service = global_role_service
        self.list_role_service = list_role_service
        self.notification_service = NotificationService()

    def _check_list_participant(self, list_id: int, user_internal_id: int):
        if not self.list_role_service.user_has_access(user_internal_id, list_id):
            raise ForbiddenException("You don't have access to this list")
        
        db_list = self.list_repository.get_by_id(list_id)
        if not db_list:
            raise NotFoundException("List not found")
        
        return db_list

    def _check_lock(self, list_id: int, user_internal_id: int):
        from app.services.lock_service import LockService
        lock_service = LockService(self.db)
        if not lock_service.check_lock(list_id, user_internal_id):
            raise LockException("List is locked by another user")

    def get_items_by_list(self, list_id: int, user_internal_id: int) -> TypeList[ItemInDB]:
        self._check_list_participant(list_id, user_internal_id)
        
        items = self.item_repository.get_all_by_list(list_id)
        return [ItemInDB.model_validate(item) for item in items]
    
    def create_item(self, list_id: int, item_create: ItemCreate, user_internal_id: int) -> ItemInDB:
        if not self.list_role_service.user_has_access(user_internal_id, list_id):
            raise ForbiddenException("No access to this list")
        
        if not self.list_repository.get_by_id(list_id):
            raise NotFoundException("List not found")
        
        item_data = item_create.model_dump(exclude_unset=True)
        new_item = self.item_repository.create(list_id, item_data)
        
        logger.info(f"Created item {new_item.id} in list {list_id} by user {user_internal_id}")
        return ItemInDB.model_validate(new_item)

    def get_item(self, list_id: int, item_id: int, user_internal_id: int) -> ItemInDB:
        if not self.list_role_service.user_has_access(user_internal_id, list_id):
            raise ForbiddenException("No access to this list")
        
        item = self.item_repository.get_by_id(list_id, item_id)
        if not item:
            raise NotFoundException("Item not found")
        
        return ItemInDB.model_validate(item)

    def get_all_items(self, list_id: int, user_internal_id: int) -> TypeList[ItemInDB]:
        if not self.list_role_service.user_has_access(user_internal_id, list_id):
            raise ForbiddenException("No access to this list")
        
        items = self.item_repository.get_all_by_list(list_id)
        return [ItemInDB.model_validate(item) for item in items]

    def update_item(self, list_id: int, item_id: int, item_update: ItemUpdate, user_internal_id: int) -> ItemInDB:
        if not self.list_role_service.user_has_access(user_internal_id, list_id):
            raise ForbiddenException("No access to this list")
        
        current_item = self.item_repository.get_by_id(list_id, item_id)
        if not current_item:
            raise NotFoundException("Item not found")
        
        update_data = item_update.model_dump(exclude_unset=True)
        self._validate_item_update_permissions(user_internal_id, list_id, update_data)
        
        updated_item = self.item_repository.update(item_id, update_data)
        if not updated_item:
            raise NotFoundException("Item not found")
        
        logger.info(f"Updated item {item_id} in list {list_id} by user {user_internal_id}")
        return ItemInDB.model_validate(updated_item)

    def delete_item(self, list_id: int, item_id: int, user_internal_id: int) -> Dict[str, str]:
        # Access is checked by `require_list_access` in the endpoint.
        # Any participant can delete items as per README.
        success = self.item_repository.delete(list_id, item_id)
        if not success:
            raise NotFoundException("Item not found")

        logger.info(f"Deleted item {item_id} from list {list_id} by user {user_internal_id}")
        return {"message": "Item deleted successfully"}

    def _validate_item_update_permissions(self, user_internal_id: int, list_id: int, update_data: Dict[str, Any]) -> None:
        if not self.list_role_service.user_has_access(user_internal_id, list_id):
            raise ForbiddenException("No access to this list")
        
        global_role = self.global_role_service.get_role(user_internal_id)
        global_role_type = global_role.role_type if global_role else None
        
        restricted_fields = []
        
        if 'price' in update_data and global_role_type != GlobalRoleType.CLIENT:
            restricted_fields.append('price (requires CLIENT global role)')
        
        if 'quantity' in update_data and global_role_type != GlobalRoleType.WORKER:
            restricted_fields.append('quantity (requires WORKER global role)')
        
        if restricted_fields:
            raise ForbiddenException(f"Additional global role restrictions: {', '.join(restricted_fields)}")
        
        logger.debug(f"User {user_internal_id} with global role {global_role_type} validated for item update")
