from sqlalchemy.orm import Session
from app.models.project_model import Project
from app.schemas.project_schema import ProjectCreate, ProjectUpdate
from .base_repository import BaseRepository

class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(Project, db)
