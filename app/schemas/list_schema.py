
from typing import List as TypeList, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from .item_schema import ItemInDB

class ListBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    destination_address: Optional[str] = Field(None, max_length=255)
    project_id: int

class ListCreate(ListBase):
    pass

class ListUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    destination_address: Optional[str] = Field(None, max_length=255)

class ListInDB(BaseModel):
    id: int
    name: str = Field(..., min_length=1)
    project_id: int
    created_at: datetime
    updated_at: datetime
    destination_address: Optional[str] = None
    items: TypeList[ItemInDB] = []
    
    model_config = ConfigDict(from_attributes=True)
