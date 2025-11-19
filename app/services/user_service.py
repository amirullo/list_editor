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

    def get_or_create_user_by_external_id(self, external_id: str) -> User:
        return self.user_repository.get_or_create_by_external_id(external_id)

    def get_user_by_internal_id(self, internal_id: UUID) -> Optional[User]: # Changed type to UUID
        return self.user_repository.get_by_internal_id(internal_id)
