from app.repositories.lock_repository import LockRepository
from app.repositories.list_repository import ListRepository
from app.repositories.project_repository import ProjectRepository
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
        lock_repo: Optional[LockRepository] = None,
        list_repo: Optional[ListRepository] = None,
        project_repo: Optional[ProjectRepository] = None
    ):
        self.db = db
        self.lock_repo = lock_repo or LockRepository(db)
        self.list_repo = list_repo or ListRepository(db)
        self.project_repo = project_repo or ProjectRepository(db)
        self.notification_service = NotificationService()
    
    def _check_project_access(self, list_id: int, user_internal_id: int):
        db_list = self.list_repo.get_by_id(list_id)
        if not db_list:
            raise NotFoundException("List not found")
        
        project = self.project_repo.get_by_id_for_user(db_list.project_id, user_internal_id)
        if not project:
            raise ForbiddenException("You don't have access to this project")
        
        return db_list

    def acquire_lock(self, list_id: int, user_internal_id: int) -> Optional[Lock]:
        try:
            self._check_project_access(list_id, user_internal_id)
            
            lock = self.lock_repo.acquire_lock(list_id, user_internal_id) # Pass user_internal_id
            if lock:
                self.notification_service.notify_lock_acquired(list_id, user_internal_id)
                return lock
            else:
                raise LockException("List is already locked by another user")
                
        except (ForbiddenException, NotFoundException, LockException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error acquiring lock on list {list_id}: {str(e)}")
            raise LockException(f"Lock acquisition failed: {str(e)}")

    def release_lock(self, list_id: int, user_internal_id: int) -> Dict[str, Any]:
        try:
            self._check_project_access(list_id, user_internal_id)
            
            success = self.lock_repo.release_lock(list_id, user_internal_id) # Pass user_internal_id
            if success:
                self.notification_service.notify_lock_released(list_id, user_internal_id)
                return {"status": "success", "message": "Lock released successfully"}
            else:
                raise ForbiddenException("Lock not held by current user or not found")
                
        except (ForbiddenException, NotFoundException):
            raise
        except Exception as e:
            logger.error(f"Unexpected error releasing lock on list {list_id}: {str(e)}")
            return {"status": "error", "message": f"Lock release failed: {str(e)}"}

    def check_lock(self, list_id: int, user_internal_id: int) -> bool:
        try:
            self._check_project_access(list_id, user_internal_id)
            
            current_lock = self.lock_repo.get_lock_by_list_id(list_id)
            
            if not current_lock:
                return True
            
            if current_lock.holder_id == user_internal_id: # Direct comparison with int
                return True
            
            return False
            
        except (ForbiddenException, NotFoundException):
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking lock on list {list_id}: {str(e)}")
            return False
