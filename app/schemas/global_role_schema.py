from pydantic import BaseModel, ConfigDict, Field
from app.models.global_role_model import GlobalRoleType
from datetime import datetime

class GlobalRoleBase(BaseModel):
    user_id: str
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
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)