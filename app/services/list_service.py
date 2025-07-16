from typing import List as TypeList, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.list_repository import ListRepository
from app.repositories.item_repository import ItemRepository
from app.repositories.lock_repository import LockRepository
from app.models.list_model import List
from app.models.item_model import Item
from app.schemas.list_schema import ListCreate, ListUpdate
from app.schemas.item_schema import ItemCreate
from app.core.exceptions import NotFoundException, LockException
from .notification_service import NotificationService

class ListService:
    def __init__(self, db: Session):
        self.db = db
        self.list_repo = ListRepository(db)
        self.item_repo = ItemRepository(db)
        self.lock_repo = LockRepository(db)
        self.notification_service = NotificationService()
    
    def get_list(self, list_id: int) -> List:
        list_obj = self.list_repo.get(list_id)
        if not list_obj:
            raise NotFoundException(f"List with id {list_id} not found")
        return list_obj
    
    def get_all_lists(self) -> TypeList[List]:
        return self.list_repo.get_all()
    
    def create_list(self, list_create: ListCreate, items: TypeList[ItemCreate] = None) -> List:
        # Create list data
        list_data = list_create.dict()
        
        # Create items data if provided
        items_data = []
        if items:
            items_data = [item.dict() for item in items]
        
        # Create list with items
        list_obj = self.list_repo.create_with_items(list_data, items_data)
        
        # Send notification
        self.notification_service.send_notification(f"List '{list_obj.name}' created successfully")
        
        return list_obj
    
    def update_list(self, list_id: int, user_id: str, list_update: ListUpdate) -> List:
        # Check if list exists
        list_obj = self.get_list(list_id)
        
        # Check if list is locked by someone else
        lock = self.lock_repo.get_lock_by_list_id(list_id)
        if lock and lock.holder_id != user_id:
            raise LockException()
        
        # Update list
        updated_list = self.list_repo.update(list_obj, list_update.dict(exclude_unset=True))
        
        # Send notification
        self.notification_service.send_notification(f"List '{updated_list.name}' updated successfully")
        
        return updated_list
    
    def delete_list(self, list_id: int, user_id: str) -> Dict[str, Any]:
        # Check if list exists
        list_obj = self.get_list(list_id)
        
        # Check if list is locked by someone else
        lock = self.lock_repo.get_lock_by_list_id(list_id)
        if lock and lock.holder_id != user_id:
            raise LockException()
        
        # Delete list
        deleted_list = self.list_repo.delete(list_id)
        
        # Release any locks on this list
        if lock:
            self.lock_repo.delete(lock.id)
        
        # Send notification
        self.notification_service.send_notification(f"List '{deleted_list.name}' deleted successfully")
        
        return {"status": "success", "message": "List deleted successfully"}