import uuid
from sqlalchemy import Column, String, Float, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel

class List(BaseModel):
    __tablename__ = "lists"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    
    items = relationship("Item", back_populates="list", cascade="all, delete-orphan")
    
class Item(BaseModel):
    __tablename__ = "items"
    
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    list_id = Column(String(36), ForeignKey("lists.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=True)
    
    list = relationship("List", back_populates="items")

    # __table_args__ = (
    #     UniqueConstraint('list_id', 'name', name='uq_item_name_per_list'),
    # )