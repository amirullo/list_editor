from typing import List as TypeList, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.item_repository import ItemRepository
from app.schemas.item_schema import ItemCreate, ItemUpdate
from app.models.list_model import Item
from app.core.exceptions import NotFoundException
from .notification_service import NotificationService
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logger import logger

class ItemService:
    def __init__(self, db: Session):
        self.db = db
        self.item_repo = ItemRepository(db)
        self.notification_service = NotificationService()
    
    def get_item(self, list_id: str, item_id: str) -> Item:
        item = self.item_repo.get_by_id(list_id, item_id)
        if not item:
            raise NotFoundException(f"Item with id {item_id} not found in list {list_id}")
        return item
    
    def get_items_by_list(self, list_id: str) -> TypeList[Item]:
        return self.item_repo.get_all_by_list(list_id)
    
    def create_item(self, list_id: str, item_create: ItemCreate) -> Item:
        try:
            # Create item
            item = self.item_repo.create(list_id, item_create.dict())
            
            # Send notification
            self.notification_service.send_notification(f"Item '{item.name}' added to list")
            
            logger.info(f"Item '{item.name}' created successfully in list {list_id}")
            return item
        except SQLAlchemyError as e:
            logger.error(f"Database error while creating item: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while creating item: {str(e)}")
            raise
    
    def update_item(self, list_id: str, item_id: str, item_update: ItemUpdate) -> Item:
        updated_item = self.item_repo.update(list_id, item_id, item_update.dict(exclude_unset=True))
        if not updated_item:
            raise NotFoundException(f"Item with id {item_id} not found in list {list_id}")
        
        # Send notification
        self.notification_service.send_notification(f"Item '{updated_item.name}' updated successfully")
        
        return updated_item
    
    def delete_item(self, list_id: str, item_id: str) -> Dict[str, Any]:
        if not self.item_repo.delete(list_id, item_id):
            raise NotFoundException(f"Item with id {item_id} not found in list {list_id}")
        
        # Send notification
        self.notification_service.send_notification(f"Item '{item_id}' deleted from list")
        
        return {"status": "success", "message": "Item deleted successfully"}