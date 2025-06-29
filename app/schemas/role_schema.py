from pydantic import BaseModel
from app.models.role_model import RoleType

class RoleBase(BaseModel):
    role_type: RoleType

class RoleCreate(RoleBase):
    pass

class RoleInDB(RoleBase):
    id: str

    class Config:
        orm_mode = True