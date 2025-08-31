from typing import List as TypeList, Optional, Dict, Any
from app.models.list_model import List
from app.models.item_model import Item
from app.models.list_user_model import ListUser
from .base_repository import BaseRepository
from sqlalchemy.orm import Session
from app.utils.uuid_generator import generate_uuid


class ListRepository(BaseRepository[List]):
    def __init__(self, db: Session):
        super().__init__(List, db)

    def create_with_items(self, list_data: Dict[str, Any], creator_id: str, items_data: TypeList[Dict[str, Any]] = None) -> List:
        """Create list with optional items"""
        # Create the list
        # list_data['id'] = generate_uuid()
        list_data['name'] = ''
        db_list = List(**list_data)
        self.db.add(db_list)
        self.db.flush()  # Get the ID

        # Add items if provided
        if items_data:
            for item_data in items_data:
                item_data['id'] = generate_uuid()
                item_data['list_id'] = db_list.id
                db_item = Item(**item_data)
                self.db.add(db_item)

        self.db.commit()
        self.db.refresh(db_list)
        return db_list

    def get_user_lists(self, user_id: str) -> TypeList[List]:
        """Get all lists user has access to"""
        result = self.db.query(List).join(ListUser).filter(ListUser.user_id == user_id).all()
        return result

    def get_list_by_id_and_user(self, list_id: int, user_id: str) -> Optional[List]:
        return self.db.query(List).join(ListUser).filter(
            List.id == list_id,
            ListUser.user_id == user_id
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