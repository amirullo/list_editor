from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel
import enum

class ProjectRoleType(str, enum.Enum):
    CREATOR = "CREATOR"
    USER = "USER"

class ProjectUser(BaseModel):
    __tablename__ = "project_users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    role_type = Column(Enum(ProjectRoleType), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="project_users")
    project = relationship("Project", back_populates="project_users")

    @property
    def user_external_id(self) -> str:
        return self.user.external_id
