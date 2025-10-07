from typing import List as TypeList, Optional, Dict, Any
from app.models.list_model import List
from app.models.list_user_model import ListUser
from .base_repository import BaseRepository
from sqlalchemy.orm import Session

class ListRepository(BaseRepository[List]):
    def __init__(self, db: Session):
        super().__init__(List, db)

    def get_user_lists(self, user_internal_id: int) -> TypeList[List]:
        """Get all lists user has access to"""
        return self.db.query(List).join(ListUser).filter(ListUser.user_id == user_internal_id).all()

    def get_list_by_id(self, list_id: int, user_internal_id: int) -> Optional[List]:
        return self.db.query(List).join(ListUser).filter(
            List.id == list_id,
            ListUser.user_id == user_internal_id
        ).first()

    def update(self, list_id: int, list_update: Dict[str, Any]) -> Optional[List]:
        db_list = self.get_by_id(list_id)
        if not db_list:
            return None
        
        for key, value in list_update.items():
            if hasattr(db_list, key):
                setattr(db_list, key, value)
        
        self.db.commit()
        self.db.refresh(db_list)
        return db_list
