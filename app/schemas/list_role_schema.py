from pydantic import BaseModel, ConfigDict
from app.models.list_role_model import ListRoleType
from datetime import datetime

class ListRoleBase(BaseModel):
    user_id: str
    list_id: int
    role: ListRoleType

class ListParticipant(BaseModel):
    user_id: str
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