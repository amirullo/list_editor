from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

class StatusMessage(BaseModel):
    message: str
    status: str = "success"

class ResponseModel(BaseModel, Generic[T]):
    data: Optional[T] = None
    message: str = "Success"
    status: str = "success"
    
    class Config:
        arbitrary_types_allowed = True