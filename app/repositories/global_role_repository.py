from sqlalchemy.orm import Session
from app.models.global_role_model import GlobalRole, GlobalRoleType
from typing import Optional
# from uuid import UUID # Removed UUID import

class GlobalRoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_internal_id(self, user_internal_id: int) -> Optional[GlobalRole]: # Changed type to int
        """Get global role by user internal ID"""
        return self.db.query(GlobalRole).filter(GlobalRole.user_id == user_internal_id).first()

    def create(self, role_data: dict) -> GlobalRole:
        """Create new global role"""
        role = GlobalRole(**role_data)
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def create_or_update(self, user_internal_id: int, role_type: GlobalRoleType) -> GlobalRole: # Changed type to int
        """Create or update user global role"""
        existing_role = self.get_by_user_internal_id(user_internal_id)
        if existing_role:
            existing_role.role_type = role_type
            self.db.commit()
            self.db.refresh(existing_role)
            return existing_role
        else:
            role_data = {"user_id": user_internal_id, "role_type": role_type}
            return self.create(role_data)

    def delete(self, user_internal_id: int) -> bool: # Changed type to int
        """Delete user's global role"""
        role = self.get_by_user_internal_id(user_internal_id)
        if role:
            self.db.delete(role)
            self.db.commit()
            return True
        return False
