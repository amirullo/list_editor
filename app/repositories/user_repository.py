from .base_repository import BaseRepository
from app.models.user_model import User
from sqlalchemy.orm import Session
from typing import Optional

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_if_not_exists(self, user_id: str) -> User:
        existing_user = self.get_by_id(user_id)
        if existing_user:
            return existing_user
        
        new_user = User(id=user_id)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user