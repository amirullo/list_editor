from pydantic import BaseModel, Field
from typing import Optional

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
    id: str
    list_id: str

    class Config:
        orm_mode = True