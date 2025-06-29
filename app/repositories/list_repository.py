from typing import List as TypeList, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.list_model import List, Item
from .base_repository import BaseRepository

class ListRepository(BaseRepository[List]):
    def __init__(self, db: Session):
        super().__init__(List, db)
        
    def create_with_items(self, list_data: Dict[str, Any], items_data: TypeList[Dict[str, Any]]) -> List:
        # Create the list
        db_list = self.create(list_data)
        
        # Create items associated with the list
        for item_data in items_data:
            item_data["list_id"] = db_list.id
            db_item = Item(**item_data)
            self.db.add(db_item)
        
        self.db.commit()
        self.db.refresh(db_list)
        return db_list

class ItemRepository(BaseRepository[Item]):
    def __init__(self, db: Session):
        super().__init__(Item, db)
    
    def get_items_by_list(self, list_id: str) -> TypeList[Item]:
        return self.db.query(Item).filter(Item.list_id == list_id).all()