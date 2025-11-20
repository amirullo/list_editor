from sqlalchemy.orm import Session, joinedload
from typing import List as TypeList, Optional
from app.models.project_model import Project
from app.models.project_user_model import ProjectUser, ProjectRoleType
from app.models.user_model import User
from app.schemas.project_schema import ProjectCreate, ProjectUpdate
from .base_repository import BaseRepository
from app.repositories.user_repository import UserRepository # Import UserRepository

class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(Project, db)
        self.user_repository = UserRepository(db) # Initialize UserRepository

    def get_all_for_user(self, user_internal_id: int) -> TypeList[Project]: # Changed type to int
        return self.db.query(Project).options(joinedload(Project.project_users).joinedload(ProjectUser.user)).join(ProjectUser).filter(ProjectUser.user_id == user_internal_id).all()

    def get_by_id_for_user(self, project_id: int, user_internal_id: int) -> Optional[Project]: # Changed type to int
        return self.db.query(Project).options(joinedload(Project.project_users).joinedload(ProjectUser.user)).join(ProjectUser).filter(
            Project.id == project_id,
            ProjectUser.user_id == user_internal_id
        ).first()

    def add_user_to_project(self, project: Project, user_internal_id: int, role: ProjectRoleType) -> Optional[ProjectUser]: # Changed user: User to user_internal_id: int
        project_user = ProjectUser(user_id=user_internal_id, project_id=project.id, role_type=role)
        self.db.add(project_user)
        self.db.commit()
        self.db.refresh(project_user)
        return project_user

    def remove_user_from_project(self, project: Project, user_internal_id: int) -> bool: # Changed user: User to user_internal_id: int
        project_user = self.db.query(ProjectUser).filter(
            ProjectUser.project_id == project.id,
            ProjectUser.user_id == user_internal_id
        ).first()
        if project_user:
            self.db.delete(project_user)
            self.db.commit()
            return True
        return False

    def get_project_users(self, project_id: int) -> TypeList[ProjectUser]:
        return self.db.query(ProjectUser).filter(ProjectUser.project_id == project_id).all()
