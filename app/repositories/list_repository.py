from typing import List as TypeList, Optional, Dict, Any
from app.models.list_model import List
from app.models.item_model import Item
from app.models.user_model import User
from .base_repository import BaseRepository
from sqlalchemy.orm import Session

class ListRepository(BaseRepository[List]):
    def __init__(self, db: Session):
        super().__init__(List, db)

    def create_with_items(self, list_data: Dict[str, Any], creator_id: str, items_data: TypeList[Dict[str, Any]] = None) -> List:
        # Create the list
        db_list = List(**list_data, creator_id=creator_id)
        self.db.add(db_list)
        self.db.flush()  # Get the ID
        
        # Add creator as a user of the list
        self._ensure_user_exists(creator_id)
        creator = self.db.query(User).filter(User.id == creator_id).first()
        if creator:
            db_list.users.append(creator)  # Fix: use users instead of user_ids
        
        # Add items if provided
        if items_data:
            for item_data in items_data:
                db_item = Item(**item_data, list_id=db_list.id)
                self.db.add(db_item)
        
        self.db.commit()
        self.db.refresh(db_list)
        return db_list

    def get_user_lists(self, user_id: str) -> TypeList[List]:
        return self.db.query(List).join(List.users).filter(User.id == user_id).all()  # Fix: use users

    def get_list_by_id_and_user(self, list_id: int, user_id: str) -> Optional[List]:
        """Get list by ID if user has access"""
        self._ensure_user_exists(user_id)
        return self.db.query(List).filter(
            List.id == list_id,
            List.users.any(User.id == user_id)
        ).first()

    def get_list_by_id_and_creator(self, list_id: int, creator_id: str) -> Optional[List]:
        return self.db.query(List).filter(
            List.id == list_id,
            List.creator_id == creator_id
        ).first()

    def update(self, list_id: int, list_update: Dict[str, Any]) -> List:
        db_list = self.db.query(List).filter(List.id == list_id).first()
        if not db_list:
            return None
        
        for key, value in list_update.items():
            if hasattr(db_list, key):
                setattr(db_list, key, value)
        
        self.db.commit()
        self.db.refresh(db_list)
        return db_list

    def add_user_to_list(self, list_id: int, user_id: str) -> List:
        db_list = self.db.query(List).filter(List.id == list_id).first()
        if not db_list:
            return None
        
        # Ensure user exists
        self._ensure_user_exists(user_id)
        user = self.db.query(User).filter(User.id == user_id).first()
        
        # Check if user is already in the list
        if user not in db_list.users:  # Fix: use users
            db_list.users.append(user)  # Fix: use users
            self.db.commit()
            self.db.refresh(db_list)
        
        return db_list

    def remove_user_from_list(self, list_id: int, user_id: str) -> List:
        db_list = self.db.query(List).filter(List.id == list_id).first()
        if not db_list:
            return None
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if user and user in db_list.users:  # Fix: use users
            db_list.users.remove(user)  # Fix: use users
            self.db.commit()
            self.db.refresh(db_list)
        
        return db_list

    def _ensure_user_exists(self, user_id: str):
        """Ensure a user exists in the database, create if not"""
        existing_user = self.db.query(User).filter(User.id == user_id).first()
        if not existing_user:
            new_user = User(id=user_id)
            self.db.add(new_user)
            self.db.flush()
