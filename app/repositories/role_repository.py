from sqlalchemy.orm import Session
from app.models.role_model import Role
from .base_repository import BaseRepository

class RoleRepository(BaseRepository[Role]):
    def __init__(self, db: Session):
        super().__init__(Role, db)