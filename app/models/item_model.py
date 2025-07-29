
from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Item(BaseModel):
    __tablename__ = "items"

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=True)
    list_id = Column(Integer, ForeignKey('lists.id'), nullable=False)

    # Relationships
    list = relationship("List", back_populates="items")
