from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import BaseModel

class Lock(BaseModel):
    __tablename__ = "locks"
    
    id = Column(Integer, primary_key=True, index=True)
    list_id = Column(Integer, ForeignKey("lists.id"), nullable=False, unique=True)
    holder_id = Column(Integer, ForeignKey("users.internal_id"), nullable=False)
    acquired_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    list = relationship("List", back_populates="lock")
    holder = relationship("User")
