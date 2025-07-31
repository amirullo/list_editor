from typing import Optional
from app.models.list_role_model import ListRoleType
from app.repositories.list_user_repository import ListUserRepository
from app.utils.logger import logger

class ListRoleService:
    def __init__(self, list_user_repository: ListUserRepository):
        self.list_user_repository = list_user_repository

    def get_user_role_in_list(self, user_id: str, list_id: int) -> Optional[ListRoleType]:
        """Get user's role in specific list"""
        list_user = self.list_user_repository.get_by_user_and_list(user_id, list_id)
        if not list_user:
            return None
        return list_user.role.role_type

    def add_user_to_list(self, user_id: str, list_id: int, role_type: ListRoleType = ListRoleType.USER):
        """Add user to list with specified role"""
        return self.list_user_repository.create(user_id, list_id, role_type)

    def check_list_permission(self, user_id: str, list_id: int, required_role: ListRoleType) -> bool:
        """Check if user has required role in list"""
        return self.list_user_repository.user_has_role(user_id, list_id, required_role)

    def user_has_access(self, user_id: str, list_id: int) -> bool:
        """Check if user has any access to the list"""
        return self.list_user_repository.get_by_user_and_list(user_id, list_id) is not None

    def is_creator(self, user_id: str, list_id: int) -> bool:
        """Check if user is creator of the list"""
        list_user = self.list_user_repository.get_by_user_and_list(user_id, list_id)
        if not list_user:
            return False
        return list_user.role.role_type == ListRoleType.CREATOR