from typing import Optional
from app.models.global_role_model import GlobalRole, GlobalRoleType
from app.repositories.global_role_repository import GlobalRoleRepository
from app.schemas.global_role_schema import GlobalRoleCreate, GlobalRoleInDB
from app.utils.logger import logger

class GlobalRoleService:
    def __init__(self, global_role_repository: GlobalRoleRepository):
        self.global_role_repository = global_role_repository

    def get_role(self, user_id: int) -> Optional[GlobalRole]: # Changed user_id type hint to int
        """Get user's global role"""
        return self.global_role_repository.get_by_user_internal_id(user_id) # Corrected method name

    def create_role(self, user_id: int, role_type: GlobalRoleType) -> GlobalRole: # Changed user_id type hint to int
        """Create or update user's global role"""
        role = self.global_role_repository.create_or_update(user_id, role_type)
        logger.info(f"Created/updated global role {role_type.value} for user {user_id}")
        return role

    def check_permission(self, user_id: int, required_role: GlobalRoleType) -> bool: # Changed user_id type hint to int
        """Check if user has required global role"""
        user_role = self.get_role(user_id)
        if not user_role:
            return False
        return user_role.role_type == required_role

    def assign_client_role(self, user_id: int) -> GlobalRole: # Changed user_id type hint to int
        """Assign CLIENT role to user"""
        return self.create_role(user_id, GlobalRoleType.CLIENT)

    def assign_worker_role(self, user_id: int) -> GlobalRole: # Changed user_id type hint to int
        """Assign WORKER role to user"""
        return self.create_role(user_id, GlobalRoleType.WORKER)