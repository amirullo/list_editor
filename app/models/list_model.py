import uuid
from sqlalchemy import Column, String, Float, Integer, ForeignKey, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel

class List(BaseModel):
    __tablename__ = "lists"
    
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    
    items = relationship("Item", back_populates="list", cascade="all, delete-orphan")
    
# class Item(BaseModel):
#     __tablename__ = "items"
#
#     item_id = Column(Integer, autoincrement=True, primary_key=True)
#     list_id = Column(Integer, ForeignKey("lists.id"), nullable=False)
#     name = Column(String(255), nullable=False)
#     category = Column(String(255), nullable=True)
#     quantity = Column(Integer, nullable=False, default=1)
#     price = Column(Float, nullable=True)
#
#     list = relationship("List", back_populates="items")
