from app.repositories.list_user_repository import ListUserRepository
from app.models.list_role_model import ListRoleType
from typing import Optional

class ListRoleService:
    def __init__(self, list_user_repo: ListUserRepository):
        self.list_user_repo = list_user_repo

    def get_user_role_in_list(self, user_id: str, list_id: int) -> Optional[ListRoleType]:
        list_user = self.list_user_repo.get_by_user_and_list(user_id, list_id)
        return list_user.role if list_user else None

    async def user_has_access_to_list(self, user_id: str, list_id: int) -> bool:
        """Check if the user has any role in the list."""
        role = self.get_user_role_in_list(user_id, list_id)
        return role is not None

    async def is_user_list_creator(self, user_id: str, list_id: int) -> bool:
        """Check if the user is the creator of the list."""
        role = self.get_user_role_in_list(user_id, list_id)
        return role == ListRoleType.CREATOR