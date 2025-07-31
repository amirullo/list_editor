from .base_repository import BaseRepository

from app.models.global_role_model import GlobalRole
from sqlalchemy.orm import Session
from typing import Optional

class UserRepository(BaseRepository[GlobalRole]):
    def __init__(self, db: Session):
        super().__init__(GlobalRole, db)

    def get_by_id(self, user_id: str) -> Optional[GlobalRole]:
        return self.db.query(GlobalRole).filter(GlobalRole.user_id == user_id).first()

    def create_if_not_exists(self, user_id: str) -> GlobalRole:
        """Create user if doesn't exist"""
        existing = self.db.query(GlobalRole).filter(GlobalRole.user_id == user_id).first()
        if not existing:
            user = GlobalRole(user_id=user_id)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        return existing