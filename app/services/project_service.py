from sqlalchemy.orm import Session
from app.repositories.project_repository import ProjectRepository
from app.schemas.project_schema import ProjectCreate, ProjectUpdate
from app.models.project_model import Project

class ProjectService:
    def __init__(self, db: Session):
        self.repository = ProjectRepository(db)

    def create_project(self, project: ProjectCreate) -> Project:
        return self.repository.create(obj_in=project.model_dump())

    def get_project(self, project_id: int) -> Project:
        return self.repository.get(id=project_id)

    def get_all_projects(self):
        return self.repository.get_all()

    def update_project(self, project_id: int, project: ProjectUpdate) -> Project:
        return self.repository.update(id=project_id, obj_in=project.model_dump(exclude_unset=True))

    def delete_project(self, project_id: int):
        return self.repository.delete(id=project_id)
