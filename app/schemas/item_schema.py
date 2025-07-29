from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    name: str

class ItemCreate(ItemBase):
    category: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None

class ItemUpdate(ItemBase):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None

class ItemInDB(ItemBase):
    id: int
    list_id: int
    name: str
    created_at: datetime
    updated_at: datetime
    category: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)