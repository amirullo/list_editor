from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class LockBase(BaseModel):
    list_id: int
    holder_id: int

class LockCreate(LockBase):
    pass

class LockInDB(LockBase):
    id: int
    acquired_at: datetime = datetime.now() # Added default value
    created_at: Optional[datetime] = None # Added created_at
    updated_at: Optional[datetime] = None # Added updated_at

    model_config = ConfigDict(from_attributes=True)
