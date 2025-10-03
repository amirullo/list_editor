from app.models.list_role_model import ListRole, ListRoleType
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app.models.list_user_model import ListUser
class ListUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_internal_id: int, list_id: int, role_type: ListRoleType) -> ListUser:
        # If creating a CREATOR role, ensure no other creator exists
        if role_type == ListRoleType.CREATOR:
            existing_creator = self.db.query(ListUser).join(ListRole).filter(
                ListUser.list_id == list_id,
                ListRole.role_type == ListRoleType.CREATOR
            ).first()
            if existing_creator:
                raise ValueError(f"List {list_id} already has a creator")
        
        # Check if a role with the given type exists
        role = self.db.query(ListRole).filter(ListRole.role_type == role_type).first()
        if not role:
            # This should not happen if roles are seeded
            raise ValueError(f"Role {role_type} not found")

        list_user = ListUser(user_internal_id=user_internal_id, list_id=list_id, role_id=role.id)

        self.db.add(list_user)
        self.db.commit()
        self.db.refresh(list_user)
        return list_user

    def get_by_user_and_list(self, user_internal_id: int, list_id: int) -> Optional[ListUser]:
        """Get list user relationship with role loaded"""
        return self.db.query(ListUser).filter(
            ListUser.user_internal_id == user_internal_id,
            ListUser.list_id == list_id
        ).first()

    def user_has_access(self, user_internal_id: int, list_id: int) -> bool:
        """Check if a user has any role in a list"""
        res = self.get_by_user_and_list(user_internal_id, list_id)
        return res is not None

    def remove_user_from_list(self, user_internal_id: int, list_id: int) -> bool:
        list_user = self.get_by_user_and_list(user_internal_id, list_id)
        if list_user:
            self.db.delete(list_user)
            self.db.commit()
            return True
        return False

    def get_creator_by_list_id(self, list_id: int) -> Optional[ListUser]:
        """Get the creator (user with CREATOR role) for a specific list"""
        return self.db.query(ListUser).join(ListRole).filter(
            ListUser.list_id == list_id,
            ListRole.role_type == ListRoleType.CREATOR
        ).first()

    def get_users_by_list_id(self, list_id: int) -> List[ListUser]:
        """Get all users who have access to a specific list"""
        return self.db.query(ListUser).filter(ListUser.list_id == list_id).all()
