from pydantic import BaseModel, ConfigDict, Field
from app.models.global_role_model import GlobalRoleType
from datetime import datetime
from typing import Optional

class GlobalRoleBase(BaseModel):
    role: GlobalRoleType = Field(..., alias='role_type')

    model_config = ConfigDict(
        from_attributes=True,  # Allow creating schema from ORM model
        populate_by_name=True, # Allow populating 'role_type' from 'role' in request
    )

class GlobalRoleCreate(GlobalRoleBase):
    pass

class GlobalRoleUpdate(GlobalRoleBase):
    pass

class GlobalRoleInDB(GlobalRoleBase):
    id: int
    user_internal_id: int = Field(..., alias='user_id') # Explicitly add user_internal_id
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GlobalRoleResponse(BaseModel):
    message: str
    data: Optional[GlobalRoleInDB] = None
