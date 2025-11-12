from typing import Optional
from uuid import UUID

from app.models.user_model import User
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate # Import UserCreate


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_user_by_external_id(self, external_id: str) -> Optional[User]:
        return self.user_repository.get_by_external_id(external_id)

    def create_user(self, external_id: str) -> User:
        # Create a UserCreate object before passing it to the repository
        user_create_schema = UserCreate(external_id=external_id)
        return self.user_repository.create(user_create_schema)

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        return self.user_repository.get_by_id(user_id)
