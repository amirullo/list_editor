from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class ListRoleType(enum.Enum):
    CREATOR = "creator"
    USER = "user"

class ListRole(BaseModel):
    __tablename__ = "list_roles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_type = Column(Enum(ListRoleType), nullable=False, unique=True)
    description = Column(String, nullable=True)

    list_users = relationship("ListUser", back_populates="role")