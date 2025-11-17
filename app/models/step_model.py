from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
from .project_model import Project

class Step(Base):
    __tablename__ = "steps"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    planned_start_date = Column(DateTime(timezone=True))
    planned_end_date = Column(DateTime(timezone=True))
    actual_start_date = Column(DateTime(timezone=True))
    actual_end_date = Column(DateTime(timezone=True))
    materials_price = Column(Float)
    workers_price = Column(Float)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    parent_step_id = Column(Integer, ForeignKey("steps.id"))
    
    project = relationship("Project", back_populates="steps")
    parent_step = relationship("Step", remote_side=[id])
    sub_steps = relationship("Step", back_populates="parent_step")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

Project.steps = relationship("Step", order_by=Step.id, back_populates="project")
