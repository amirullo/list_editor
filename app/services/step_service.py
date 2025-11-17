from sqlalchemy.orm import Session
from app.repositories.step_repository import StepRepository
from app.schemas.step_schema import StepCreate, StepUpdate
from app.models.step_model import Step

class StepService:
    def __init__(self, db: Session):
        self.repository = StepRepository(db)

    def create_step(self, step: StepCreate) -> Step:
        return self.repository.create(obj_in=step.model_dump())

    def get_step(self, step_id: int) -> Step:
        return self.repository.get(id=step_id)

    def get_all_steps(self):
        return self.repository.get_all()

    def update_step(self, step_id: int, step: StepUpdate) -> Step:
        return self.repository.update(id=step_id, obj_in=step.model_dump(exclude_unset=True))

    def delete_step(self, step_id: int) -> bool:
        return self.repository.delete(id=step_id)
