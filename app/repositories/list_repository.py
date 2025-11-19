
from typing import List as TypeList, Optional, Dict, Any
from app.models.list_model import List
from app.models.project_user_model import ProjectUser
from .base_repository import BaseRepository
from sqlalchemy.orm import Session

class ListRepository(BaseRepository[List]):
    def __init__(self, db: Session):
        super().__init__(List, db)

    def get_by_id(self, list_id: int) -> Optional[List]:
        return self.db.query(List).filter(List.id == list_id).first()

    def get_by_id_for_user(self, list_id: int, user_internal_id: int) -> Optional[List]:
        return self.db.query(List).join(ProjectUser, List.project_id == ProjectUser.project_id).filter(
            List.id == list_id,
            ProjectUser.user_id == user_internal_id
        ).first()

    def get_all_for_project(self, project_id: int) -> TypeList[List]:
        return self.db.query(List).filter(List.project_id == project_id).all()

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
