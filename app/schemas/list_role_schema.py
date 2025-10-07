from pydantic import BaseModel, ConfigDict, Field
from app.models.list_role_model import ListRoleType
from datetime import datetime

class ListRoleBase(BaseModel):
    user_internal_id: int = Field(..., alias='user_id')
    list_id: int
    role: ListRoleType

class ListParticipant(BaseModel):
    user_internal_id: int = Field(..., alias='user_id')
    role: ListRoleType

class ListRoleCreate(ListRoleBase):
    pass

class ListRoleUpdate(BaseModel):
    role: ListRoleType

class ListRoleInDB(ListRoleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)