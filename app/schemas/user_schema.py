from pydantic import BaseModel, ConfigDict, Field

class UserBase(BaseModel):
    external_id: str = Field(..., description="User's unique external identifier")

class UserCreate(UserBase):
    pass

class UserResponse(BaseModel):
    id: int
    external_id: str

    model_config = ConfigDict(from_attributes=True)
