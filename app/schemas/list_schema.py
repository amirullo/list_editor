from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid
from app.schemas.item_schema import ItemInDB


# List schemas
class ListBase(BaseModel):
    name: str

class ListCreate(ListBase):
    pass

class ListUpdate(BaseModel):
    name: Optional[str] = None

class ListInDB(ListBase):
    id: int
    created_at: datetime
    updated_at: datetime
    items: List[ItemInDB] = []

    model_config = ConfigDict(from_attributes=True)