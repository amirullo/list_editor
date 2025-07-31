from pydantic import BaseModel
from app.models.list_role_model import ListRoleType
from typing import Optional

class ListRoleBase(BaseModel):
    role_type: ListRoleType

class ListRoleCreate(ListRoleBase):
    user_id: str
    list_id: int

class ListRoleUpdate(BaseModel):
    role_type: Optional[ListRoleType] = None

class ListRoleInDB(ListRoleBase):
    id: int
    user_id: str
    list_id: int
    
    class Config:
        from_attributes = True

# For API responses showing list participants
class ListParticipant(BaseModel):
    user_id: str
    role_type: ListRoleType
    
    class Config:
        from_attributes = True