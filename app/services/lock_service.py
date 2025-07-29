from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.repositories.lock_repository import LockRepository
from app.repositories.list_repository import ListRepository
from app.core.exceptions import LockException, NotFoundException
from app.models.lock_model import Lock
from .notification_service import NotificationService

class LockService:
    def __init__(self, db: Session, lock_repo: LockRepository = None):
        self.db = db
        self.lock_repo = lock_repo or LockRepository(db)
        self.list_repo = ListRepository(db)
        self.notification_service = NotificationService()
    
    def _check_list_participant(self, list_id: int, user_id: str):
        """Check if user is a participant in the list"""
        db_list = self.list_repo.get_list_by_id_and_user(list_id, user_id)
        if not db_list:
            raise NotFoundException(f"List {list_id} not found or user {user_id} has no access")
        return db_list

    def acquire_lock(self, list_id: int, user_id: str) -> Optional[Lock]:
        """Acquire lock for list editing (FIFO mechanism as per README)"""
        try:
            # Check if user has access to the list
            self._check_list_participant(list_id, user_id)
            
            # Try to acquire lock
            lock = self.lock_repo.acquire_lock(list_id, user_id)
            if lock:
                # Notify other users about lock acquisition
                self.notification_service.send_notification(
                    user_id, 
                    f"You have acquired edit lock for list {list_id}",
                    "lock_acquired"
                )
                return lock
            else:
                raise LockException(f"Failed to acquire lock for list {list_id}")
        except Exception as e:
            raise LockException(f"Lock acquisition failed: {str(e)}")

    def release_lock(self, list_id: int, user_id: str) -> Dict[str, Any]:
        """Release lock for list"""
        try:
            # Check if user has access to the list
            self._check_list_participant(list_id, user_id)
            
            success = self.lock_repo.release_lock(list_id, user_id)
            if success:
                # Notify user about lock release
                self.notification_service.send_notification(
                    user_id,
                    f"Edit lock released for list {list_id}",
                    "lock_released"
                )
                return {"status": "success", "message": "Lock released successfully"}
            else:
                return {"status": "error", "message": "Failed to release lock or lock not held by user"}
        except Exception as e:
            return {"status": "error", "message": f"Lock release failed: {str(e)}"}

    def check_lock(self, list_id: int, user_id: str) -> bool:
        """Check if user holds the lock for the list"""
        try:
            lock = self.lock_repo.get_lock_by_list_id(list_id)
            if not lock:
                return False
            return lock.holder_id == user_id
        except Exception:
            return False