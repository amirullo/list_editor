from sqlalchemy.orm import Session
from typing import Optional
from app.models.role_model import Role
from .base_repository import BaseRepository

class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: Session):
        super().__init__(Role, db)
    
    def get_by_user_id(self, user_id: str) -> Optional[Role]:
        """Get role by user ID"""
        return self.db.query(Role).filter(Role.user_id == user_id).first()
    
    def create_or_update(self, user_id: str, role_type) -> Role:
        """Create or update user role"""
        existing_role = self.get_by_user_id(user_id)
        if existing_role:
            existing_role.role_type = role_type
            self.db.commit()
            self.db.refresh(existing_role)
            return existing_role
        else:
            role_data = {"user_id": user_id, "role_type": role_type}
            return self.create(role_data)