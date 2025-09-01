# This file should exist if LockService is being used
from .base_repository import BaseRepository
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional

# If Lock model exists, import it
try:
    from app.models.lock_model import Lock
    
    class LockRepository(BaseRepository[Lock]):
        def __init__(self, db: Session):
            super().__init__(Lock, db)
        
        def get_lock_by_list_id(self, list_id: int) -> Optional[Lock]:
            return self.db.query(Lock).filter(Lock.list_id == list_id).first()

        def acquire_lock(self, list_id: int, holder_id: str) -> Optional[Lock]:
            try:
                lock = Lock(list_id=list_id, holder_id=holder_id)
                self.db.add(lock)
                self.db.commit()
                self.db.refresh(lock)
                return lock
            except IntegrityError:
                self.db.rollback()
                # Lock already exists, so we can't acquire it.
                # The caller should handle the case where a lock is already held.
                return None

        def release_lock(self, list_id: int, holder_id: str) -> bool:
            lock = self.db.query(Lock).filter(
                Lock.list_id == list_id,
                Lock.holder_id == holder_id
            ).first()

            if lock:
                self.db.delete(lock)
                self.db.commit()
                return True
            return False

except ImportError:
    # Lock model does not exist, LockRepository will not be defined.
    pass