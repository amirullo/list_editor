from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar('T')

class StatusMessage(BaseModel):
    message: str

class Response(GenericModel, Generic[T]):
    status: str = "success"
    message: str = "Operation successful"
    data: Optional[T] = None