from typing import List as TypeList, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from .item_schema import ItemInDB

class ListBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

class ListCreate(ListBase):
    user_id_list: Optional[TypeList[str]] = Field(default_factory=list)

class ListUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    user_id_list: Optional[TypeList[str]] = None

class ListInDB(ListBase):
    id: int
    creator_id: str
    user_id_list: TypeList[str]
    created_at: datetime
    updated_at: datetime
    items: TypeList[ItemInDB] = []

    class Config:
        from_attributes = True

class ListAddUser(BaseModel):
    user_id: str = Field(..., min_length=1)

class ListRemoveUser(BaseModel):
    user_id: str = Field(..., min_length=1)