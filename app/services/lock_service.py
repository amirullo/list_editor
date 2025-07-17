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
    
    def acquire_lock(self, list_id: int, user_id: str) -> Optional[Lock]:
        lock = self.lock_repo.acquire_lock(list_id, user_id)
        if lock:
            self.notification_service.notify_lock_acquired(list_id, user_id)
            return lock
        else:
            return None  # Lock acquisition failed
    
    def release_lock(self, list_id: int, user_id: str) -> Dict[str, Any]:
        if self.lock_repo.release_lock(list_id, user_id):
            self.notification_service.notify_lock_released(list_id, user_id)
            return {"status": "success", "message": "Lock released successfully"}
        else:
            return {"status": "error", "message": "Failed to release lock"}
    
    def check_lock(self, list_id: int, user_id: str) -> bool:
        lock = self.lock_repo.get_lock_by_list_id(list_id)
        if not lock:
            return True  # Not locked, free to edit
        return lock.holder_id == user_id  # True if user holds the lock