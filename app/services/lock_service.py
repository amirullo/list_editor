from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.lock_repository import LockRepository
from app.core.exceptions import LockException
from app.models.lock_model import Lock
from .notification_service import NotificationService

class LockService:
    def __init__(self, db: Session):
        self.db = db
        self.lock_repo = LockRepository(db)
        self.notification_service = NotificationService()
    
    def acquire_lock(self, list_id: int, user_id: str) -> Lock:
        # Try to acquire the lock
        lock = self.lock_repo.acquire_lock(list_id, user_id)
        if not lock:
            # Check if current user already holds the lock
            existing_lock = self.lock_repo.get_lock_by_list_id(list_id)
            if existing_lock and existing_lock.holder_id == user_id:
                return existing_lock
            
            # List is locked by someone else
            raise LockException()
        
        # Send notification
        self.notification_service.send_notification(f"Lock acquired on list")
        
        return lock
    
    def release_lock(self, list_id: int, user_id: str) -> Dict[str, Any]:
        # Try to release the lock
        success = self.lock_repo.release_lock(list_id, user_id)
        if not success:
            raise LockException("You don't have a lock on this list or the lock doesn't exist")
        
        # Send notification
        self.notification_service.send_notification(f"Lock released on list")
        
        return {"status": "success", "message": "Lock released successfully"}
    
    def check_lock(self, list_id: int, user_id: str) -> bool:
        lock = self.lock_repo.get_lock_by_list_id(list_id)
        if not lock:
            return True  # Not locked, free to edit
        return lock.holder_id == user_id  # True if user holds the lock