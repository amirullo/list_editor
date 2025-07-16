from typing import List as TypeList, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.item_repository import ItemRepository
from app.repositories.lock_repository import LockRepository
from app.schemas.item_schema import ItemCreate, ItemUpdate, ItemInDB
from app.schemas.list_schema import ListCreate, ListUpdate
from app.models.item_model import Item
from app.core.exceptions import NotFoundException, LockException
from .notification_service import NotificationService
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logger import logger


class ItemService:
    def __init__(self, db: Session):
        self.db = db
        self.item_repo = ItemRepository(db)
        self.lock_repo = LockRepository(db)
        self.notification_service = NotificationService()
    
    def get_item(self, list_id: int, item_id: int) -> Item:
        item = self.item_repo.get_by_id(list_id, item_id)
        if not item:
            raise NotFoundException(f"Item with id {item_id} not found in list {list_id}")
        return item
    
    def get_items_by_list(self, list_id: int) -> TypeList[Item]:
        return self.item_repo.get_all_by_list(list_id)
    
    def create_item(self, list_id: int, item_create: ItemCreate) -> ItemInDB:
        try:
            # Create item
            item = self.item_repo.create(list_id, item_create.model_dump(exclude_unset=True))
            
            # Send notification
            self.notification_service.send_notification(f"Item '{item.name}' added to list")
            
            logger.info(f"Item '{item.name}' created successfully in list {list_id}")
            return ItemInDB.model_validate(item)
        except SQLAlchemyError as e:
            logger.error(f"Database error while creating item: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while creating item: {str(e)}")
            raise
    
    def update_item(self, list_id: int, item_id: int, item_update: ItemUpdate, user_id: str) -> Item:

        # Check if list exists
        # list_obj = self.get_list(list_id)
        item_obj = self.get_item(list_id, item_id)

        # Check if list is locked by someone else
        lock = self.lock_repo.get_lock_by_list_id(list_id)
        if lock and lock.holder_id != user_id:
            raise LockException()

        # Update Item
        # updated_list = self.item_repo.update(item_obj, list_update.model_dump(exclude_unset=True))
        updated_item = self.item_repo.update(list_id, item_id, item_update.model_dump(exclude_unset=True))

        if not updated_item:
            raise NotFoundException(f"Item with id {item_id} not found in list {list_id}")
        
        if lock:
            self.lock_repo.delete(lock.id)
        # Send notification
        self.notification_service.send_notification(f"Item '{updated_item.name}' updated successfully")
        
        return updated_item
    
    def delete_item(self, list_id: int, item_id: int) -> Dict[str, Any]:
        if not self.item_repo.delete(list_id, item_id):
            raise NotFoundException(f"Item with id {item_id} not found in list {list_id}")
        
        # Send notification
        self.notification_service.send_notification(f"Item '{item_id}' deleted from list")
        
        return {"status": "success", "message": "Item deleted successfully"}