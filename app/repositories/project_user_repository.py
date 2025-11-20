from sqlalchemy.orm import Session
from app.models.project_user_model import ProjectUser
from .base_repository import BaseRepository

class ProjectUserRepository(BaseRepository[ProjectUser]):
    def __init__(self, db: Session):
        super().__init__(ProjectUser, db)
