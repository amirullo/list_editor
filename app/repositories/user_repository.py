from sqlalchemy.orm import Session
from typing import Optional
from .base_repository import BaseRepository
from app.models.user_model import User
from app.schemas.user_schema import UserCreate

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_external_id(self, external_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.external_id == external_id).first()

    def create(self, user_create: UserCreate) -> User:
        user = User(external_id=user_create.external_id)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_or_create_by_external_id(self, external_id: str) -> User:
        user = self.get_by_external_id(external_id)
        if not user:
            user = self.create(UserCreate(external_id=external_id))
        return user
    
    def get_by_internal_id(self, internal_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == internal_id).first()
