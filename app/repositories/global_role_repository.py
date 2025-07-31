from sqlalchemy.orm import Session
from app.models.global_role_model import GlobalRole, GlobalRoleType
from typing import Optional

class GlobalRoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: str) -> Optional[GlobalRole]:
        """Get global role by user ID"""
        return self.db.query(GlobalRole).filter(GlobalRole.user_id == user_id).first()

    def create(self, role_data: dict) -> GlobalRole:
        """Create new global role"""
        role = GlobalRole(**role_data)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def create_or_update(self, user_id: str, role_type: GlobalRoleType) -> GlobalRole:
        """Create or update user global role"""
        existing_role = self.get_by_user_id(user_id)
        if existing_role:
            existing_role.role_type = role_type
            self.db.commit()
            self.db.refresh(existing_role)
            return existing_role
        else:
            role_data = {"user_id": user_id, "role_type": role_type}
            return self.create(role_data)

    def delete(self, user_id: str) -> bool:
        """Delete user's global role"""
        role = self.get_by_user_id(user_id)
        if role:
            self.db.delete(role)
            self.db.commit()
            return True
        return False