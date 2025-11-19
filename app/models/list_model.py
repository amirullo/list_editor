from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import BaseModel

class List(BaseModel):
    __tablename__ = "lists"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    destination_address = Column(String, nullable=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    
    items = relationship("Item", back_populates="list", cascade="all, delete-orphan")
    project = relationship("Project", back_populates="lists")
    lock = relationship("Lock", uselist=False, back_populates="list", cascade="all, delete-orphan")
