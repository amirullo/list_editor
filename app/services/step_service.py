from sqlalchemy.orm import Session
from app.repositories.step_repository import StepRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.step_schema import StepCreate, StepUpdate
from app.models.step_model import Step
from app.core.exceptions import NotFoundException

class StepService:
    def __init__(self, db: Session):
        self.repository = StepRepository(db)
        self.project_repository = ProjectRepository(db)

    def create_step(self, step: StepCreate) -> Step:
        project = self.project_repository.get(id=step.project_id)
        if not project:
            raise NotFoundException("Project not found")
        return self.repository.create(obj_in=step.model_dump())

    def get_step(self, step_id: int) -> Step:
        step = self.repository.get(id=step_id)
        if not step:
            raise NotFoundException("Step not found")
        return step

    def get_all_steps(self):
        return self.repository.get_all()

    def update_step(self, step_id: int, step: StepUpdate) -> Step:
        updated_step = self.repository.update(id=step_id, obj_in=step.model_dump(exclude_unset=True))
        if not updated_step:
            raise NotFoundException("Step not found")
        return updated_step

    def delete_step(self, step_id: int) -> bool:
        was_deleted = self.repository.delete(id=step_id)
        if not was_deleted:
            raise NotFoundException("Step not found")
        return was_deleted
