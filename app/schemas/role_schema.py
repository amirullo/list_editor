from pydantic import BaseModel, ConfigDict
from app.models.role_model import RoleType

class RoleBase(BaseModel):
    role_type: RoleType

class RoleCreate(RoleBase):
    pass

class RoleInDB(RoleBase):
    id: str

    model_config = ConfigDict(from_attributes=True)