from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.role_repository import RoleRepository
from app.models.role_model import Role, RoleType
from app.core.exceptions import PermissionException

class RoleService:
    def __init__(self, db: Session):
        self.db = db
        self.role_repo = RoleRepository(db)
    
    def get_role(self, user_id: str) -> Optional[Role]:
        return self.role_repo.get(user_id)
    
    def create_role(self, user_id: str, role_type: RoleType) -> Role:
        role_data = {
            "id": user_id,
            "role_type": role_type
        }
        return self.role_repo.create(role_data)
    
    def check_permission(self, user_id: str, required_role: RoleType) -> bool:
        role = self.get_role(user_id)
        if not role:
            return False
        return role.role_type == required_role
    
    def ensure_permission(self, user_id: str, required_role: RoleType) -> None:
        if not self.check_permission(user_id, required_role):
            raise PermissionException(f"This action requires {required_role.value} role")