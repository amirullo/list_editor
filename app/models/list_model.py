from sqlalchemy import Column, Integer, String, Text, DateTime
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
    
    # Relationships
    items = relationship("Item", back_populates="list", cascade="all, delete-orphan")
    list_users = relationship("ListUser", back_populates="list", cascade="all, delete-orphan")
    locks = relationship("Lock", back_populates="list", cascade="all, delete-orphan")
