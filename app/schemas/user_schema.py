
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from .global_role_schema import GlobalRoleInDB

class UserBase(BaseModel):
    id: str = Field(..., description="User's unique identifier")

class UserCreate(UserBase):
    pass

class UserInDB(UserBase):
    created_at: datetime
    updated_at: datetime
    global_role: Optional[GlobalRoleInDB] = None

    model_config = ConfigDict(from_attributes=True)
