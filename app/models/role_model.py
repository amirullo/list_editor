from sqlalchemy import Column, String, Enum
from .base import BaseModel
import enum

class RoleType(enum.Enum):
    CLIENT = "client"
    WORKER = "worker"

class Role(BaseModel):
    __tablename__ = "roles"
    
    id = Column(String(36), primary_key=True)
    role_type = Column(Enum(RoleType), nullable=False)