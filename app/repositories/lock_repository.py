from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
import uuid
from app.models.lock_model import Lock
from app.repositories.base_repository import BaseRepository


class LockRepository(BaseRepository[Lock]):
    def __init__(self, db: Session):
        super().__init__(Lock, db)
    
    def get_lock_by_list_id(self, list_id: int) -> Optional[Lock]:
        return self.db.query(Lock).filter(Lock.list_id == list_id).first()
    
    def acquire_lock(self, list_id: int, holder_id: str) -> Optional[Lock]:
        # First check if the list is already locked
        existing_lock = self.get_lock_by_list_id(list_id)
        if existing_lock:
            return None  # Already locked
        
        # Create a new lock
        lock_data = {
            "id": str(uuid.uuid4()),
            "list_id": list_id,
            "holder_id": holder_id,
            "acquired_at": datetime.now()
        }
        return self.create(lock_data)
    
    def release_lock(self, list_id: int, holder_id: str) -> bool:
        lock = self.get_lock_by_list_id(list_id)
        if lock and lock.holder_id == holder_id:
            self.db.delete(lock)
            self.db.commit()
            return True
        return False