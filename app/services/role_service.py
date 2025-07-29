from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.role_repository import RoleRepository
from app.models.role_model import RoleType
from app.schemas.role_schema import RoleCreate, RoleInDB
from app.core.exceptions import PermissionException

class RoleService:
    def __init__(self, db: Session):
        self.db = db
        self.role_repo = RoleRepository(db)
    
    def get_role(self, user_id: str) -> Optional[RoleInDB]:
        """Get user role"""
        role = self.role_repo.get_by_user_id(user_id)
        if role:
            return RoleInDB.model_validate(role)
        return None
    
    def create_role(self, user_id: str, role_type: RoleType) -> RoleInDB:
        """Create a new role for user"""
        role_data = RoleCreate(user_id=user_id, role_type=role_type)
        role = self.role_repo.create(role_data.model_dump())
        return RoleInDB.model_validate(role)
    
    def check_permission(self, user_id: str, required_role: RoleType) -> bool:
        role = self.get_role(user_id)
        if not role:
            return False
        return role.role_type == required_role
    
    def ensure_permission(self, user_id: str, required_role: RoleType) -> None:
        if not self.check_permission(user_id, required_role):
            raise PermissionException(f"This action requires {required_role.value} role")
