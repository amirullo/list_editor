from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel

class Project(BaseModel):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    place_description = Column(String)
    planned_start_date = Column(DateTime(timezone=False))
    planned_end_date = Column(DateTime(timezone=False))
    actual_start_date = Column(DateTime(timezone=False))
    actual_end_date = Column(DateTime(timezone=False))
    total_materials_price = Column(Float)
    total_workers_price = Column(Float)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())

    lists = relationship("List", back_populates="project")
    project_users = relationship("ProjectUser", back_populates="project", cascade="all, delete-orphan")
