from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    quantity: int = Field(1, ge=0) # Added quantity field
    price: Optional[float] = Field(None, gt=0)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    quantity: Optional[int] = Field(None, ge=0) # Added quantity field
    price: Optional[float] = Field(None, gt=0)

class ItemInDB(ItemBase):
    id: int
    list_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)