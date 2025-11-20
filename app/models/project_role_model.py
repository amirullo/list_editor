from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from .base import BaseModel
from .project_user_model import ProjectRoleType

class ProjectRole(BaseModel):
    __tablename__ = "project_roles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_type = Column(Enum(ProjectRoleType), nullable=False, unique=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
