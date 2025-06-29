from typing import List as TypeList, Dict, Any
from sqlalchemy.orm import Session
from ..repositories.list_repository import ItemRepository
from ..repositories.lock_repository import LockRepository
from ..models.list_model import Item
from ..schemas.list_schema import ItemCreate, ItemUpdate
from ..core.exceptions import ListNotFoundException, LockException
from .notification_service import NotificationService

class ItemService:
    def __init__(self, db: Session):
        self.db = db
        self.item_repo = ItemRepository(db)
        self.lock_repo = LockRepository(db)
        self.notification_service = NotificationService()
    
    def get_item(self, item_id: str) -> Item:
        item = self.item_repo.get(item_id)
        if not item:
            raise ListNotFoundException("Item not found")
        return item
    
    def get_items_by_list(self, list_id: str) -> TypeList[Item]:
        return self.item_repo.get_items_by_list(list_id)
    
    def create_item(self, list_id: str, user_id: str, item_create: ItemCreate) -> Item:
        # Check if list is locked by someone else
        lock = self.lock_repo.get_lock_by_list_id(list_id)
        if lock and lock.holder_id != user_id:
            raise LockException()
        
        # Create item data
        item_data = item_create.dict()
        item_data["list_id"] = list_id
        
        # Create item
        item = self.item_repo.create(item_data)
        
        # Send notification
        self.notification_service.send_notification(f"Item '{item.name}' added to list")
        
        return item
    
    def update_item(self, item_id: str, user_id: str, item_update: ItemUpdate) -> Item:
        # Get item
        item = self.get_item(item_id)
        
        # Check if list is locked by someone else
        lock = self.lock_repo.get_lock_by_list_id(item.list_id)
        if lock and lock.holder_id != user_id:
            raise LockException()
        
        # Update item
        updated_item = self.item_repo.update(item, item_update.dict(exclude_unset=True))
        
        # Send notification
        self.notification_service.send_notification(f"Item '{updated_item.name}' updated successfully")
        
        return updated_item
    
    def delete_item(self, item_id: str, user_id: str) -> Dict[str, Any]:
        # Get item
        item = self.get_item(item_id)
        
        # Check if list is locked by someone else
        lock = self.lock_repo.get_lock_by_list_id(item.list_id)
        if lock and lock.holder_id != user_id:
            raise LockException()
        
        # Delete item
        deleted_item = self.item_repo.delete(item_id)
        
        # Send notification
        self.notification_service.send_notification(f"Item '{deleted_item.name}' deleted from list")
        
        return {"status": "success", "message": "Item deleted successfully"}