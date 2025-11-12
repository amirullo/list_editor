from sqlalchemy.orm import Session
from app.models.item_model import Item
from typing import List as TypeList, Optional
from .base_repository import BaseRepository
from app.utils.logger import logger

class ItemRepository(BaseRepository[Item]):
    def __init__(self, db: Session):
        super().__init__(Item, db)

    def create(self, list_id: int, item_data: dict) -> Item:
        db_item = Item(list_id=list_id, **item_data)
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        logger.info(f"Created item: {db_item.__dict__}")
        return db_item

    def get_by_id(self, list_id: int, item_id: int) -> Optional[Item]:
        return self.db.query(Item).filter(
            Item.list_id == list_id,
            Item.id == item_id  # Corrected from Item.item_id
        ).first()

    def get_all_by_list(self, list_id: int) -> TypeList[Item]:
        return self.db.query(Item).filter(Item.list_id == list_id).all()

    def update(self, item_id: int, item_data: dict) -> Optional[Item]:
        db_item = self.db.query(Item).filter(Item.id == item_id).first() # Corrected from Item.item_id
        if db_item:
            for key, value in item_data.items():
                setattr(db_item, key, value)
            self.db.commit()
            self.db.refresh(db_item)
        return db_item

    def delete(self, list_id: int, item_id: int) -> bool:
        db_item = self.get_by_id(list_id, item_id)
        if db_item:
            self.db.delete(db_item)
            self.db.commit()
            return True
        return False