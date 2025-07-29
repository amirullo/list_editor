from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Association table for many-to-many relationship between lists and users
list_users = Table(
    'list_users',
    Base.metadata,
    Column('list_id', Integer, ForeignKey('lists.id'), primary_key=True),
    Column('user_id', String, ForeignKey('users.id'), primary_key=True)
)

class List(Base):
    __tablename__ = "lists"
    
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    creator_id = Column(String, nullable=False)
    
    # Relationships
    items = relationship("Item", back_populates="list", cascade="all, delete-orphan")
    users = relationship("User", secondary=list_users, back_populates="lists")