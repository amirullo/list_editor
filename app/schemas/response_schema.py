from pydantic import BaseModel, Field, ConfigDict
from typing import TypeVar, Generic, Optional

T = TypeVar('T')


class ResponseModel(BaseModel, Generic[T]):
    status: str = Field("success", description="Response status")
    data: Optional[T] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Optional message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "data": "some_payload",
                "message": "Operation successful"
            }
        }
    )


class StatusMessage(BaseModel):
    message: str