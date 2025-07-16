from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    name: str

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = Field(ge=0)
    price: Optional[float] = Field(ge=0)

class ItemInDB(ItemBase):
    item_id: int
    list_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)