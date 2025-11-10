
from app.models.list_role_model import ListRoleType
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.list_user_model import ListUser

class ListUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_internal_id: int, list_id: int, role_type: ListRoleType) -> ListUser:
        if role_type == ListRoleType.CREATOR:
            existing_creator = self.db.query(ListUser).filter(
                ListUser.list_id == list_id,
                ListUser.role_type == ListRoleType.CREATOR
            ).first()
            if existing_creator:
                raise ValueError(f"List {list_id} already has a creator")

        list_user = ListUser(user_id=user_internal_id, list_id=list_id, role_type=role_type)

        self.db.add(list_user)
        self.db.commit()
        self.db.refresh(list_user)
        return list_user

    def get_by_user_and_list(self, user_internal_id: int, list_id: int) -> Optional[ListUser]:
        return self.db.query(ListUser).filter(
            ListUser.user_id == user_internal_id,
            ListUser.list_id == list_id
        ).first()

    def user_has_access(self, user_internal_id: int, list_id: int) -> bool:
        return self.get_by_user_and_list(user_internal_id, list_id) is not None

    def user_has_role(self, user_internal_id: int, list_id: int, role_type: ListRoleType) -> bool:
        list_user = self.get_by_user_and_list(user_internal_id, list_id)
        return list_user is not None and list_user.role_type == role_type

    def remove_user_from_list(self, user_internal_id: int, list_id: int) -> bool:
        list_user = self.get_by_user_and_list(user_internal_id, list_id)
        if list_user:
            self.db.delete(list_user)
            self.db.commit()
            return True
        return False

    def get_creator_by_list_id(self, list_id: int) -> Optional[ListUser]:
        return self.db.query(ListUser).filter(
            ListUser.list_id == list_id,
            ListUser.role_type == ListRoleType.CREATOR
        ).first()

    def get_users_by_list_id(self, list_id: int) -> List[ListUser]:
        return self.db.query(ListUser).filter(ListUser.list_id == list_id).all()

    def delete(self, user_internal_id: int, list_id: int) -> bool:
        return self.remove_user_from_list(user_internal_id, list_id)
