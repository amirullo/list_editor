from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import BaseModel
from .list_model import list_users

class User(BaseModel):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)  # UUID as string
    
    # Relationships
    lists = relationship("List", secondary=list_users, back_populates="users")