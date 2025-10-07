from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
from .base import BaseModel
from .list_role_model import ListRoleType

class ListUser(BaseModel):
    __tablename__ = "list_users"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    list_id = Column(Integer, ForeignKey("lists.id"), nullable=False)
    role_type = Column(Enum(ListRoleType), nullable=False)

    __table_args__ = (UniqueConstraint('user_id', 'list_id', name='unique_user_list'),)

    user = relationship("User", back_populates="list_associations")
    list = relationship("List", back_populates="list_users")
