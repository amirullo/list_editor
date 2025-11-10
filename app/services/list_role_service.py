
from app.repositories.list_user_repository import ListUserRepository
from app.models.list_role_model import ListRoleType
from typing import Optional

class ListRoleService:
    def __init__(self, list_user_repository: ListUserRepository):
        self.list_user_repository = list_user_repository

    def get_user_role_in_list(self, user_id: int, list_id: int) -> Optional[ListRoleType]:
        list_user = self.list_user_repository.get_by_user_and_list(user_id, list_id)
        return list_user.role_type if list_user else None

    def user_has_access_to_list(self, user_id: int, list_id: int) -> bool:
        return self.list_user_repository.user_has_access(user_id, list_id)

    def is_user_list_creator(self, user_id: int, list_id: int) -> bool:
        return self.list_user_repository.user_has_role(user_id, list_id, ListRoleType.CREATOR)
