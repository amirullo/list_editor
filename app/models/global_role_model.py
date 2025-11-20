from sqlalchemy import Column, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
import enum

class GlobalRoleType(enum.Enum):
    CLIENT = "CLIENT"
    WORKER = "WORKER"

class GlobalRole(BaseModel):
    __tablename__ = "global_roles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.internal_id"), nullable=False, unique=True)
    role_type = Column(Enum(GlobalRoleType), nullable=False)

    user = relationship("User", back_populates="global_role")
