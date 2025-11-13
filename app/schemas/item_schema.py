from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    quantity: int = Field(1, ge=0)
    price: Optional[float] = Field(None, gt=0)
    item_link: Optional[str] = Field(None, max_length=255)
    item_photo_link: Optional[str] = Field(None, max_length=255)
    delivery_price: Optional[float] = Field(None, gt=0)
    delivery_period: Optional[int] = Field(None, ge=0)
    store_address: Optional[str] = Field(None, max_length=255)
    store_distance: Optional[float] = Field(None, gt=0)

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    quantity: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, gt=0)
    item_link: Optional[str] = Field(None, max_length=255)
    item_photo_link: Optional[str] = Field(None, max_length=255)
    delivery_price: Optional[float] = Field(None, gt=0)
    delivery_period: Optional[int] = Field(None, ge=0)
    store_address: Optional[str] = Field(None, max_length=255)
    store_distance: Optional[float] = Field(None, gt=0)
    approved: Optional[int] = Field(None, ge=0, le=1)
    bought: Optional[int] = Field(None, ge=0, le=1)
    delivered: Optional[int] = Field(None, ge=0, le=1)

class ItemInDB(ItemBase):
    id: int
    list_id: int
    created_at: datetime
    updated_at: datetime
    approved: int
    bought: int
    delivered: int

    model_config = ConfigDict(from_attributes=True)