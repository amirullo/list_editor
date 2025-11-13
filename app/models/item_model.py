
from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class Item(BaseModel):
    __tablename__ = "items"

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=True)
    list_id = Column(Integer, ForeignKey('lists.id'), nullable=False)
    item_link = Column(String, nullable=True)
    item_photo_link = Column(String, nullable=True)
    delivery_price = Column(Float, nullable=True)
    delivery_period = Column(Integer, nullable=True)
    store_address = Column(String, nullable=True)
    store_distance = Column(Float, nullable=True)
    approved = Column(Integer, default=0)
    bought = Column(Integer, default=0)
    delivered = Column(Integer, default=0)

    # Relationships
    list = relationship("List", back_populates="items")

