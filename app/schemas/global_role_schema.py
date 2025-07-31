from pydantic import BaseModel
from app.models.global_role_model import GlobalRoleType
from typing import Optional

class GlobalRoleBase(BaseModel):
    user_id: str
    role_type: GlobalRoleType

class GlobalRoleCreate(GlobalRoleBase):
    pass

class GlobalRoleUpdate(BaseModel):
    role_type: Optional[GlobalRoleType] = None

class GlobalRoleInDB(GlobalRoleBase):
    id: int
    
    class Config:
        from_attributes = True