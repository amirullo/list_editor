from .base_repository import BaseRepository
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from app.models.lock_model import Lock

class LockRepository(BaseRepository[Lock]):
    def __init__(self, db: Session):
        super().__init__(Lock, db)
    
    def get_lock_by_list_id(self, list_id: int) -> Optional[Lock]:
        return self.db.query(Lock).filter(Lock.list_id == list_id).first()

    def acquire_lock(self, list_id: int, holder_internal_id: int) -> Optional[Lock]:
        try:
            lock = Lock(list_id=list_id, holder_id=holder_internal_id)
            self.db.add(lock)
            self.db.commit()
            self.db.refresh(lock)
            return lock
        except IntegrityError:
            self.db.rollback()
            return None

    def release_lock(self, list_id: int, holder_internal_id: int) -> bool:
        lock = self.db.query(Lock).filter(
            Lock.list_id == list_id,
            Lock.holder_id == holder_internal_id
        ).first()

        if lock:
            self.db.delete(lock)
            self.db.commit()
            return True
        return False
