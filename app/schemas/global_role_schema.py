from pydantic import BaseModel, ConfigDict
from app.models.global_role_model import GlobalRoleType
from datetime import datetime

class GlobalRoleBase(BaseModel):
    user_id: str
    role: GlobalRoleType

class GlobalRoleCreate(GlobalRoleBase):
    pass

class GlobalRoleUpdate(BaseModel):
    role: GlobalRoleType

class GlobalRoleInDB(GlobalRoleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)