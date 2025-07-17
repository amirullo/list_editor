from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.lock_model import Lock
from sqlalchemy.exc import IntegrityError

class LockRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_lock_by_list_id(self, list_id: int) -> Lock:
        query = text("""
            SELECT * FROM locks
            WHERE list_id = :list_id
        """)
        result = self.db.execute(query, {"list_id": list_id})
        lock_data = result.fetchone()
        if lock_data:
            return Lock(**lock_data)
        return None

    def acquire_lock(self, list_id: int, holder_id: str) -> Lock:
        try:
            query = text("""
                INSERT INTO locks (list_id, holder_id)
                VALUES (:list_id, :holder_id)
            """)
            self.db.execute(query, {"list_id": list_id, "holder_id": holder_id})
            self.db.commit()
            return self.get_lock_by_list_id(list_id)
        except IntegrityError:
            self.db.rollback()
            # Lock already exists, try to update it
            update_query = text("""
                UPDATE locks
                SET holder_id = :holder_id
                WHERE list_id = :list_id AND holder_id != :holder_id
            """)
            result = self.db.execute(update_query, {"list_id": list_id, "holder_id": holder_id})
            self.db.commit()
            if result.rowcount > 0:
                return self.get_lock_by_list_id(list_id)
            else:
                return None  # Lock is held by another user

    def release_lock(self, list_id: int, holder_id: str) -> bool:
        query = text("""
            DELETE FROM locks
            WHERE list_id = :list_id AND holder_id = :holder_id
        """)
        result = self.db.execute(query, {"list_id": list_id, "holder_id": holder_id})
        self.db.commit()
        return result.rowcount > 0