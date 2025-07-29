from pydantic import BaseModel
from app.models.role_model import RoleType

class RoleBase(BaseModel):
    role_type: RoleType

class RoleCreate(RoleBase):
    pass

class RoleInDB(RoleBase):
    id: int
    user_id: str
    
    class Config:
        from_attributes = True