from typing import Optional, Dict, Any, List as TypeList
from sqlalchemy.orm import Session
from app.repositories.item_repository import ItemRepository
from app.repositories.list_repository import ListRepository
from app.schemas.item_schema import ItemCreate, ItemUpdate, ItemInDB
from app.schemas.list_schema import ListCreate, ListUpdate
from app.models.item_model import Item
from app.core.exceptions import NotFoundException, LockException, ForbiddenException
from app.services.notification_service import NotificationService
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logger import logger


class ItemService:
    def __init__(self, item_repo: ItemRepository, list_repo: ListRepository = None):
        self.item_repo = item_repo
        self.list_repo = list_repo
        self.notification_service = NotificationService()

    def _check_list_participant(self, list_id: int, user_id: str):
        """Check if user is a participant of the list"""
        if not self.list_repo:
            # If list_repo not injected, create it (this is a fallback)
            from app.core.db import get_db
            from app.repositories.list_repository import ListRepository
            db = next(get_db())
            self.list_repo = ListRepository(db)
        
        db_list = self.list_repo.get_list_by_id_and_user(list_id, user_id)
        if not db_list:
            raise ForbiddenException(f"Access denied to list {list_id}")
        return db_list

    def get_items_by_list(self, list_id: int) -> TypeList[Item]:
        return self.item_repo.get_all_by_list(list_id)
    
    def create_item(self, list_id: int, item_create: ItemCreate, user_id: str) -> ItemInDB:
        """Create item - only list participants can create items"""
        db_list = self._check_list_participant(list_id, user_id)
        
        item_data = item_create.model_dump()
        item_data['list_id'] = list_id
        
        try:
            # Create item
            db_item = self.item_repo.create(item_data)
            
            # Notify all participants about item creation
            self._notify_list_participants(db_list, f"Item '{db_item.name}' was added to list '{db_list.name}'", user_id)
            
            logger.info(f"Item '{db_item.name}' created successfully in list {list_id}")
            return ItemInDB.model_validate(db_item)
        except SQLAlchemyError as e:
            logger.error(f"Database error while creating item: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while creating item: {str(e)}")
            raise

    def update_item(self, list_id: int, item_id: int, item_update: ItemUpdate, user_id: str) -> ItemInDB:
        """Update item - only list participants can update items"""
        db_list = self._check_list_participant(list_id, user_id)
        
        # Verify item belongs to the list
        db_item = self.item_repo.get_by_id(list_id, item_id)  # Fix: use correct method
        if not db_item:
            raise NotFoundException(f"Item with id {item_id} not found in list {list_id}")
        
        update_data = {k: v for k, v in item_update.model_dump().items() if v is not None}
        updated_item = self.item_repo.update(item_id, update_data)  # Fix: correct signature
        
        # Notify all participants about item update
        self._notify_list_participants(db_list, f"Item '{updated_item.name}' was updated in list '{db_list.name}'", user_id)
        
        return ItemInDB.model_validate(updated_item)

    def delete_item(self, list_id: int, item_id: int, user_id: str) -> Dict[str, str]:
        """Delete item - only list participants can delete items"""
        db_list = self._check_list_participant(list_id, user_id)
        
        # Verify item belongs to the list
        db_item = self.item_repo.get(item_id)
        if not db_item or db_item.list_id != list_id:
            raise NotFoundException(f"Item with id {item_id} not found in list {list_id}")
        
        item_name = db_item.name
        self.item_repo.delete(item_id)
        
        # Notify all participants about item deletion
        self._notify_list_participants(db_list, f"Item '{item_name}' was deleted from list '{db_list.name}'", user_id)
        
        return {"message": f"Item '{item_name}' deleted successfully"}

    def _notify_list_participants(self, db_list, message: str, user_id: str):
        """Notify all participants about changes"""
        # Implementation for notifications
        pass