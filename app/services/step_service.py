from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories.step_repository import StepRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.step_schema import StepCreate, StepUpdate, Step as StepSchema
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.step_model import Step

class StepService:
    def __init__(self, db: Session):
        self.repository = StepRepository(db)
        self.project_repository = ProjectRepository(db)
        from app.repositories.list_repository import ListRepository
        self.list_repository = ListRepository(db)

    def create_step(self, step: StepCreate, user_internal_id: int) -> Step:
        project = self.project_repository.get_by_id_for_user(step.project_id, user_internal_id)
        if not project:
            raise NotFoundException("Project not found or you don't have access")
        
        new_step = self.repository.create(obj_in=step.model_dump())
        
        list_data = {
            "name": f"List for {new_step.name}",
            "project_id": new_step.project_id,
            "step_id": new_step.id
        }
        self.list_repository.create(list_data)
        
        return new_step

    def get_step(self, step_id: int, user_internal_id: int) -> StepSchema:
        db_step = self.repository.get(step_id)
        if not db_step:
            raise NotFoundException("Step not found")
        
        project = self.project_repository.get_by_id_for_user(db_step.project_id, user_internal_id)
        if not project:
            raise ForbiddenException("You don't have access to this project")
            
        return StepSchema.model_validate(db_step)

    def get_all_steps(self) -> List[StepSchema]:
        steps = self.repository.get_multi(skip=0, limit=10000) 
        return [StepSchema.model_validate(step) for step in steps]

    def update_step(self, step_id: int, step: StepUpdate, user_internal_id: int) -> Step:
        db_step = self.repository.get(step_id)
        if not db_step:
            raise NotFoundException("Step not found")

        project = self.project_repository.get_by_id_for_user(db_step.project_id, user_internal_id)
        if not project:
            raise ForbiddenException("You don't have access to this project")

        updated_step = self.repository.update(id=step_id, obj_in=step.model_dump(exclude_unset=True))
        if not updated_step:
            raise NotFoundException("Step not found")
        return updated_step

    def delete_step(self, step_id: int, user_internal_id: int) -> bool:
        db_step = self.repository.get(step_id)
        if not db_step:
            raise NotFoundException("Step not found")
        
        project = self.project_repository.get_by_id_for_user(db_step.project_id, user_internal_id)
        if not project:
            raise ForbiddenException("You don't have access to this project")

        was_deleted = self.repository.delete(id=step_id)
        if not was_deleted:
            raise NotFoundException("Step not found")
        return was_deleted
