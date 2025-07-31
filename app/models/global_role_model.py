from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class GlobalRoleType(enum.Enum):
    CLIENT = "client"
    WORKER = "worker"

class GlobalRole(BaseModel):
    __tablename__ = "global_roles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # ✅ Back to int
    user_id = Column(String, nullable=False, unique=True)
    role_type = Column(Enum(GlobalRoleType), nullable=False)

    list_users = relationship("ListUser", back_populates="user")