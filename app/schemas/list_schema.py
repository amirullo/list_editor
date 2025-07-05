from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

# Item schemas
class ItemBase(BaseModel):
    name: str
    category: Optional[str] = None
    quantity: int = Field(ge=0)
    price: Optional[float] = Field(ge=0)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name: Optional[str] = None
    quantity: Optional[int] = Field(ge=0, default=None)

class ItemInDB(ItemBase):
    item_id: int
    list_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# List schemas
class ListBase(BaseModel):
    name: str

class ListCreate(ListBase):
    pass

class ListUpdate(BaseModel):
    name: Optional[str] = None

class ListInDB(ListBase):
    id: str
    created_at: datetime
    updated_at: datetime
    items: List[ItemInDB] = []

    class Config:
        orm_mode = True