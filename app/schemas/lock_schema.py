from pydantic import BaseModel, ConfigDict
from datetime import datetime

class LockBase(BaseModel):
    list_id: int
    holder_id: int

class LockCreate(LockBase):
    pass

class LockInDB(LockBase):
    id: int
    acquired_at: datetime

    model_config = ConfigDict(from_attributes=True)
