from sqlalchemy import Column, String, DateTime, ForeignKey, func
from .base import BaseModel

class Lock(BaseModel):
    __tablename__ = "locks"
    
    id = Column(String(36), primary_key=True)
    list_id = Column(String(36), ForeignKey("lists.id"), nullable=False)
    holder_id = Column(String(36), nullable=False)  # The ID of who holds the lock
    acquired_at = Column(DateTime, default=func.now(), nullable=False)