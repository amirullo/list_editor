from typing import Optional, Dict, Any, List as TypeList
from sqlalchemy.orm import Session
from app.repositories.item_repository import ItemRepository
from app.repositories.list_repository import ListRepository
from app.repositories.list_user_repository import ListUserRepository
from app.schemas.item_schema import ItemCreate, ItemUpdate, ItemInDB
from app.models.item_model import Item
from app.models.list_role_model import ListRoleType
from app.models.global_role_model import GlobalRoleType
from app.core.exceptions import NotFoundException, LockException, ForbiddenException, PermissionException
from app.core.db import get_db
from app.services.notification_service import NotificationService
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logger import logger


class ItemService:
    def __init__(self, 
                 item_repository: ItemRepository,
                 list_repository: ListRepository,
                 global_role_service,
                 list_role_service):
        self.item_repository = item_repository
        self.list_repository = list_repository
        self.global_role_service = global_role_service
        self.list_role_service = list_role_service
        self.notification_service = NotificationService()

    def _check_list_participant(self, list_id: int, user_id: str):  # ✅ list_id is int
        """Check if user has access to the list"""
        if not self.list_role_service.user_has_access(user_id, list_id):
            raise ForbiddenException("You don't have access to this list")
        
        db_list = self.list_repository.get_by_id(list_id)
        if not db_list:
            raise NotFoundException("List not found")
        
        return db_list

    def _check_lock(self, list_id: int, user_id: str):  # ✅ list_id is int
        """Check if list is locked by another user"""
        from app.services.lock_service import LockService
        lock_service = LockService(self.db)
        if not lock_service.check_lock(list_id, user_id):
            raise LockException("List is locked by another user")

    def get_items_by_list(self, list_id: int, user_id: str) -> TypeList[ItemInDB]:  # ✅ list_id is int
        # Check access
        self._check_list_participant(list_id, user_id)
        
        items = self.item_repository.get_all_by_list(list_id)
        return [ItemInDB.model_validate(item) for item in items]
    
    def create_item(self, list_id: int, item_create: ItemCreate, user_id: str) -> ItemInDB:  # ✅ list_id is int
        """Create item - all list participants can create items"""
        # Check if user has access to the list
        if not self.list_role_service.user_has_access(user_id, list_id):
            raise ForbiddenException("No access to this list")
        
        # Verify list exists
        if not self.list_repository.get_by_id(list_id):
            raise NotFoundException("List not found")
        
        item_data = item_create.model_dump(exclude_unset=True)
        new_item = self.item_repository.create(list_id, item_data)
        
        logger.info(f"Created item {new_item.id} in list {list_id} by user {user_id}")
        return ItemInDB.model_validate(new_item)

    def get_item(self, list_id: int, item_id: int, user_id: str) -> ItemInDB:
        """Get item - all list participants can read items"""
        # Check if user has access to the list
        if not self.list_role_service.user_has_access(user_id, list_id):
            raise ForbiddenException("No access to this list")
        
        item = self.item_repository.get_by_id(list_id, item_id)
        if not item:
            raise NotFoundException("Item not found")
        
        return ItemInDB.model_validate(item)

    def get_all_items(self, list_id: int, user_id: str) -> TypeList[ItemInDB]:
        """Get all items in list - all list participants can read items"""
        # Check if user has access to the list
        if not self.list_role_service.user_has_access(user_id, list_id):
            raise ForbiddenException("No access to this list")
        
        items = self.item_repository.get_all_by_list(list_id)
        return [ItemInDB.model_validate(item) for item in items]

    def update_item(self, list_id: int, item_id: int, item_update: ItemUpdate, user_id: str) -> ItemInDB:
        """Update item with role-based field restrictions"""
        # Check if user has access to the list
        if not self.list_role_service.user_has_access(user_id, list_id):
            raise ForbiddenException("No access to this list")
        
        # Get current item
        current_item = self.item_repository.get_by_id(list_id, item_id)
        if not current_item:
            raise NotFoundException("Item not found")
        
        # Check permissions for specific fields
        update_data = item_update.model_dump(exclude_unset=True)
        self._validate_item_update_permissions(user_id, list_id, update_data)
        
        # Update item
        updated_item = self.item_repository.update(item_id, update_data)
        if not updated_item:
            raise NotFoundException("Item not found")
        
        logger.info(f"Updated item {item_id} in list {list_id} by user {user_id}")
        return ItemInDB.model_validate(updated_item)

    def delete_item(self, list_id: int, item_id: int, user_id: str) -> Dict[str, str]:
        """Delete item - creators have full access, users can delete items they can modify"""
        # Check if user has access to the list
        if not self.list_role_service.user_has_access(user_id, list_id):
            raise ForbiddenException("No access to this list")
        
        # Creators can delete any item
        is_creator = self.list_role_service.is_creator(user_id, list_id)
        
        if not is_creator:
            # Regular users can only delete items (basic permission check)
            user_role = self.list_role_service.get_user_role_in_list(user_id, list_id)
            if user_role != ListRoleType.USER:
                raise ForbiddenException("Insufficient permissions to delete item")
        
        success = self.item_repository.delete(list_id, item_id)
        if not success:
            raise NotFoundException("Item not found")
        
        logger.info(f"Deleted item {item_id} from list {list_id} by user {user_id}")
        return {"message": "Item deleted successfully"}

    def _validate_item_update_permissions(self, user_id: str, list_id: int, update_data: Dict[str, Any]) -> None:
        """Validate permissions for specific item fields based on global and list roles"""
        # First check if user has access to the list (list role check)
        if not self.list_role_service.user_has_access(user_id, list_id):
            raise ForbiddenException("No access to this list")
        
        # Get user's global role
        global_role = self.global_role_service.get_role(user_id)
        global_role_type = global_role.role_type if global_role else None
        
        # Check ADDITIONAL restrictions from global roles
        restricted_fields = []
        
        # Price field - ADDITIONAL restriction: only CLIENT can modify
        if 'price' in update_data and global_role_type != GlobalRoleType.CLIENT:
            restricted_fields.append('price (requires CLIENT global role)')
        
        # Quantity field - ADDITIONAL restriction: only WORKER can modify
        if 'quantity' in update_data and global_role_type != GlobalRoleType.WORKER:
            restricted_fields.append('quantity (requires WORKER global role)')
        
        # All other fields (name, description, etc.) are allowed for any list participant
        # No additional global restrictions
        
        if restricted_fields:
            raise ForbiddenException(f"Additional global role restrictions: {', '.join(restricted_fields)}")
        
        logger.debug(f"User {user_id} with global role {global_role_type} validated for item update")

    def update_item_price(self, list_id: int, item_id: int, price: float, user_id: str) -> ItemInDB:
        """Update item price - requires list access + CLIENT global role"""
        # Check if user has access to the list (list role check)
        if not self.list_role_service.user_has_access(user_id, list_id):
            raise ForbiddenException("No access to this list")
        
        # Check ADDITIONAL restriction from global role - only CLIENT can change price
        global_role = self.global_role_service.get_role(user_id)
        global_role_type = global_role.role_type if global_role else None
        
        if global_role_type != GlobalRoleType.CLIENT:
            raise ForbiddenException("Additional restriction: only users with CLIENT global role can change item price")
        
        # Update price
        update_data = {"price": price}
        updated_item = self.item_repository.update(item_id, update_data)
        if not updated_item:
            raise NotFoundException("Item not found")
        
        logger.info(f"Updated item {item_id} price to {price} by user {user_id}")
        return ItemInDB.model_validate(updated_item)

    def update_item_quantity(self, list_id: int, item_id: int, quantity: int, user_id: str) -> ItemInDB:
        """Update item quantity - requires list access + WORKER global role"""
        # Check if user has access to the list (list role check)
        if not self.list_role_service.user_has_access(user_id, list_id):
            raise ForbiddenException("No access to this list")
        
        # Check ADDITIONAL restriction from global role - only WORKER can change quantity
        global_role = self.global_role_service.get_role(user_id)
        global_role_type = global_role.role_type if global_role else None
        
        if global_role_type != GlobalRoleType.WORKER:
            raise ForbiddenException("Additional restriction: only users with WORKER global role can change item quantity")
        
        # Update quantity
        update_data = {"quantity": quantity}
        updated_item = self.item_repository.update(item_id, update_data)
        if not updated_item:
            raise NotFoundException("Item not found")
        
        logger.info(f"Updated item {item_id} quantity to {quantity} by user {user_id}")
        return ItemInDB.model_validate(updated_item)

    def _notify_list_participants(self, db_list, message: str, user_id: str):
        """Notify all participants about changes"""
        # Implementation for notifications
        pass