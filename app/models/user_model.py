from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    internal_id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String, unique=True, index=True, nullable=False)

    global_role = relationship("GlobalRole", back_populates="user", uselist=False)
    project_users = relationship("ProjectUser", back_populates="user")
