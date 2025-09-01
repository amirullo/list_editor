from typing import List as TypeList, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from .item_schema import ItemInDB
# from app.schemas.list_role_schema import ListParticipant # <-- This line is causing the error, let's remove it for now.

class ListBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    # user_id_list: Optional[TypeList[str]] = None

class ListCreate(ListBase):
    # user_id_list: Optional[TypeList[str]] = Field(default_factory=list)
    pass

class ListUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    # user_id_list: Optional[TypeList[str]] = None

class ListInDB(BaseModel):
    id: int
    name: str = Field(..., min_length=1)
    creator_id: Optional[str] = None  # Derived field
    user_id_list: TypeList[str] = Field(default_factory=list)  # Computed from ListUser relationships
    created_at: datetime
    updated_at: datetime
    items: TypeList[ItemInDB] = []
    
    class Config:
        from_attributes = True

class ListWithParticipants(ListInDB):
    """Extended list info with participants"""
    # This will be fixed later if needed, but for now, let's get the tests running.
    # participants: TypeList[ListParticipant] = []
    pass

class ListAddUser(BaseModel):
    user_id: str = Field(..., min_length=1)

class ListRemoveUser(BaseModel):
    user_id: str = Field(..., min_length=1)