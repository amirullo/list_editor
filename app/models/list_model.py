import uuid
from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class List(BaseModel):
    __tablename__ = "lists"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    items = relationship("Item", back_populates="list", cascade="all, delete-orphan")
    
class Item(BaseModel):
    __tablename__ = "items"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    list_id = Column(String(36), ForeignKey("lists.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=True)
    
    list = relationship("List", back_populates="items")