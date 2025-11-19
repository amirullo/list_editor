from sqlalchemy.orm import Session
from typing import List as TypeList
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.schemas.project_schema import ProjectCreate, ProjectUpdate, Project as ProjectSchema
from app.models.project_model import Project
from app.models.project_user_model import ProjectRoleType
from app.core.exceptions import NotFoundException, ForbiddenException
from app.utils.logger import logger # Import logger
# from uuid import UUID # Import UUID - Removed UUID import as internal_id is int

class ProjectService:
    def __init__(self, db: Session):
        self.repository = ProjectRepository(db)
        self.user_repository = UserRepository(db)

    def create_project(self, project: ProjectCreate, user_internal_id: int) -> Project: # Changed type to int
        new_project = self.repository.create(obj_in=project.model_dump())
        self.repository.add_user_to_project(new_project, user_internal_id, ProjectRoleType.CREATOR) # Pass internal_id
        self.repository.db.refresh(new_project) # Refresh after adding creator
        return new_project

    def get_project(self, project_id: int, user_internal_id: int) -> ProjectSchema: # Changed type to int
        project = self.repository.get_by_id_for_user(project_id, user_internal_id)
        if not project:
            raise NotFoundException("Project not found or you don't have access")
        return ProjectSchema.model_validate(project)

    def get_all_projects_for_user(self, user_internal_id: int) -> TypeList[ProjectSchema]: # Changed type to int
        projects = self.repository.get_all_for_user(user_internal_id)
        return [ProjectSchema.model_validate(p) for p in projects]

    def update_project(self, project_id: int, project: ProjectUpdate, user_internal_id: int) -> Project: # Changed type to int
        db_project = self.repository.get_by_id_for_user(project_id, user_internal_id)
        if not db_project:
            raise ForbiddenException("You don't have access to this project")

        updated_project = self.repository.update(id=project_id, obj_in=project.model_dump(exclude_unset=True))
        if not updated_project:
            raise NotFoundException("Project not found")
        return updated_project

    def delete_project(self, project_id: int, user_internal_id: int) -> bool: # Changed type to int
        db_project = self.repository.get_by_id_for_user(project_id, user_internal_id)
        if not db_project:
            raise ForbiddenException("You don't have access to this project")

        was_deleted = self.repository.delete(id=project_id)
        if not was_deleted:
            raise NotFoundException("Project not found")
        return was_deleted

    def add_user_to_project(self, project_id: int, user_external_id: str, requester_internal_id: int) -> ProjectSchema: # Changed type to int
        logger.info(f"add_user_to_project: project_id={project_id}, user_external_id={user_external_id}, requester_internal_id={requester_internal_id}")
        
        project = self.repository.get_by_id_for_user(project_id, requester_internal_id)
        if not project:
            raise ForbiddenException("You don't have access to this project")

        user_to_add = self.user_repository.get_by_external_id(user_external_id)
        if not user_to_add:
            raise NotFoundException("User to add not found")

        logger.info(f"Before adding user, project_users: {[pu.user_id for pu in project.project_users]}")
        self.repository.add_user_to_project(project, user_to_add.internal_id, ProjectRoleType.USER) # Pass internal_id
        
        # Re-fetch the project to ensure all relationships are eagerly loaded for Pydantic serialization
        project = self.repository.get_by_id_for_user(project_id, requester_internal_id)
        if not project: # Should not happen if add_user_to_project succeeded
            raise NotFoundException("Project not found after adding user")

        logger.info(f"Before Pydantic validation, SQLAlchemy project.project_users: {project.project_users}")
        for pu in project.project_users:
            logger.info(f"  SQLAlchemy ProjectUser: id={pu.id}, user_id={pu.user_id}, role_type={pu.role_type}, user_external_id={pu.user_external_id if hasattr(pu, 'user_external_id') else 'N/A'}")

        validated_project = ProjectSchema.model_validate(project)
        logger.info(f"Validated ProjectSchema project_users: {validated_project.project_users}") # Changed to project_users
        return validated_project

    def remove_user_from_project(self, project_id: int, user_external_id: str, requester_internal_id: int) -> ProjectSchema: # Changed type to int
        logger.info(f"remove_user_from_project: project_id={project_id}, user_external_id={user_external_id}, requester_internal_id={requester_internal_id}")
        
        project = self.repository.get_by_id_for_user(project_id, requester_internal_id)
        if not project:
            raise ForbiddenException("You don't have access to this project")

        user_to_remove = self.user_repository.get_by_external_id(user_external_id)
        if not user_to_remove:
            raise NotFoundException("User to remove not found")

        logger.info(f"Before removing user, project_users: {[pu.user_id for pu in project.project_users]}")
        self.repository.remove_user_from_project(project, user_to_remove.internal_id) # Pass internal_id
        
        # Re-fetch the project to ensure all relationships are eagerly loaded for Pydantic serialization
        project = self.repository.get_by_id_for_user(project_id, requester_internal_id)
        if not project: # Should not happen if remove_user_from_project succeeded
            raise NotFoundException("Project not found after removing user")
        
        logger.info(f"Before Pydantic validation, SQLAlchemy project.project_users: {project.project_users}")
        for pu in project.project_users:
            logger.info(f"  SQLAlchemy ProjectUser: id={pu.id}, user_id={pu.user_id}, role_type={pu.role_type}, user_external_id={pu.user_external_id if hasattr(pu, 'user_external_id') else 'N/A'}")
        
        validated_project = ProjectSchema.model_validate(project)
        logger.info(f"Validated ProjectSchema project_users: {validated_project.project_users}") # Changed to project_users
        return validated_project
