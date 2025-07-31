from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import BaseModel

class ListUser(BaseModel):
    __tablename__ = "list_users"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(String, ForeignKey("global_roles.user_id"), nullable=False)
    list_id = Column(Integer, ForeignKey("lists.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("list_roles.id"), nullable=False)

    # Ensure one user can have only one role per list
    __table_args__ = (UniqueConstraint('user_id', 'list_id', name='unique_user_list'),)

    # Relationships
    user = relationship("GlobalRole", back_populates="list_users")
    list = relationship("List", back_populates="list_users")
    role = relationship("ListRole", back_populates="list_users")
