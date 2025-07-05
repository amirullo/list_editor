from sqlalchemy.orm import Session
from app.models.list_model import Item
from typing import List as TypeList, Optional

class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, list_id: str, item_data: dict) -> Item:
        db_item = Item(list_id=list_id, **item_data)
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item

    def get_by_id(self, list_id: str, item_id: int) -> Optional[Item]:
        return self.db.query(Item).filter(Item.item_id == item_id, Item.list_id == list_id).first()

    def get_all_by_list(self, list_id: str) -> TypeList[Item]:
        return self.db.query(Item).filter(Item.list_id == list_id).all()

    def update(self, list_id: str, item_id: int, item_data: dict) -> Optional[Item]:
        db_item = self.get_by_id(list_id, item_id)
        if db_item:
            for key, value in item_data.items():
                setattr(db_item, key, value)
            self.db.commit()
            self.db.refresh(db_item)
        return db_item

    def delete(self, list_id: str, item_id: int) -> bool:
        db_item = self.get_by_id(list_id, item_id)
        if db_item:
            self.db.delete(db_item)
            self.db.commit()
            return True
        return False