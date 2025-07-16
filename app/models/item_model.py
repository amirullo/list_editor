
from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Item(BaseModel):
    __tablename__ = "items"

    item_id = Column(Integer, autoincrement=True, primary_key=True)
    list_id = Column(Integer, ForeignKey("lists.id"), nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(255), nullable=True)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=True)

    list = relationship("List", back_populates="items")
