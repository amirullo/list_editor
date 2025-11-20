from typing import Optional
from app.models.global_role_model import GlobalRole, GlobalRoleType
from app.repositories.global_role_repository import GlobalRoleRepository
from app.schemas.global_role_schema import GlobalRoleCreate, GlobalRoleInDB

class GlobalRoleService:
    def __init__(self, global_role_repository: GlobalRoleRepository):
        self.global_role_repository = global_role_repository

    def get_role(self, user_internal_id: int) -> Optional[GlobalRole]:
        """Get user's global role"""
        return self.global_role_repository.get_by_user_internal_id(user_internal_id)

    def create_role(self, user_internal_id: int, role_type: GlobalRoleType) -> GlobalRole:
        """Create or update user's global role"""
        role = self.global_role_repository.create_or_update(user_internal_id, role_type)
        return role

    def delete_role(self, user_internal_id: int) -> bool:
        """Delete user's global role"""
        deleted = self.global_role_repository.delete(user_internal_id)
        return deleted

    def check_permission(self, user_internal_id: int, required_role: GlobalRoleType) -> bool:
        """Check if user has required global role"""
        user_role = self.get_role(user_internal_id)
        if not user_role:
            return False
        return user_role.role_type == required_role

    def assign_client_role(self, user_internal_id: int) -> GlobalRole:
        """Assign CLIENT role to user"""
        return self.create_role(user_internal_id, GlobalRoleType.CLIENT)

    def assign_worker_role(self, user_internal_id: int) -> GlobalRole:
        """Assign WORKER role to user"""
        return self.create_role(user_internal_id, GlobalRoleType.WORKER)
