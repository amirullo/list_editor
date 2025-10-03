from app.repositories.lock_repository import LockRepository
from app.repositories.list_user_repository import ListUserRepository
from typing import Optional, Dict, Any
from app.core.exceptions import LockException, NotFoundException, ForbiddenException
from .notification_service import NotificationService
from app.models.lock_model import Lock
from app.utils.logger import logger
from sqlalchemy.orm import Session

class LockService:
    def __init__(
        self, 
        db: Session, 
        lock_repo: LockRepository = None,
        list_user_repo: ListUserRepository = None
    ):
        self.db = db
        self.lock_repo = lock_repo or LockRepository(db)
        self.list_user_repo = list_user_repo or ListUserRepository(db)
        self.notification_service = NotificationService()
    
    def _check_list_participant(self, list_id: int, user_id: str):  # ✅ list_id is int
        """Check if user has access to the list"""
        if not self.list_user_repo.user_has_access(user_id, list_id):
            raise ForbiddenException("You don't have access to this list")
        
        from app.repositories.list_repository import ListRepository
        list_repo = ListRepository(self.db)
        db_list = list_repo.get_by_id(list_id)
        if not db_list:
            raise NotFoundException("List not found")
        
        return db_list

    def acquire_lock(self, list_id: int, user_id: str) -> Optional[Lock]:  # ✅ list_id is int
        """Acquire lock on a list"""
        try:
            # Check if user has access to the list
            self._check_list_participant(list_id, user_id)
            
            # Try to acquire lock
            lock = self.lock_repo.acquire_lock(list_id, user_id)
            if lock:
                # Notify other participants
                self.notification_service.notify_lock_acquired(list_id, user_id)
                logger.info(f"Lock acquired on list {list_id} by user {user_id}")
                return lock
            else:
                raise LockException("List is already locked by another user")
                
        except (ForbiddenException, NotFoundException, LockException):
            # Re-raise our custom exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error acquiring lock on list {list_id}: {str(e)}")
            raise LockException(f"Lock acquisition failed: {str(e)}")

    def release_lock(self, list_id: int, user_id: str) -> Dict[str, Any]:  # ✅ list_id is int
        """Release lock on a list"""
        try:
            # Check if user has access to the list
            self._check_list_participant(list_id, user_id)
            
            # Try to release lock
            success = self.lock_repo.release_lock(list_id, user_id)
            if success:
                # Notify other participants
                self.notification_service.notify_lock_released(list_id, user_id)
                logger.info(f"Lock released on list {list_id} by user {user_id}")
                return {"status": "success", "message": "Lock released successfully"}
            else:
                return {"status": "error", "message": "No lock found or you don't own the lock"}
                
        except (ForbiddenException, NotFoundException):
            # Re-raise our custom exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error releasing lock on list {list_id}: {str(e)}")
            return {"status": "error", "message": f"Lock release failed: {str(e)}"}

    def check_lock(self, list_id: int, user_id: str) -> bool:  # ✅ list_id is int
        """Check if user can modify the list (either no lock or user owns the lock)"""
        try:
            # Check if user has access to the list
            self._check_list_participant(list_id, user_id)
            
            # Get current lock
            current_lock = self.lock_repo.get_lock_by_list_id(list_id)
            
            # No lock exists - user can modify
            if not current_lock:
                return True
            
            # User owns the lock - user can modify
            if current_lock.holder_id == user_id:
                return True
            
            # Someone else owns the lock - user cannot modify
            return False
            
        except (ForbiddenException, NotFoundException):
            # If user doesn't have access or list doesn't exist, they can't modify
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking lock on list {list_id}: {str(e)}")
            return False