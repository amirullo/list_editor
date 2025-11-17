from sqlalchemy.orm import Session
from app.models.step_model import Step
from app.schemas.step_schema import StepCreate, StepUpdate
from .base_repository import BaseRepository

class StepRepository(BaseRepository[Step]):
    def __init__(self, db: Session):
        super().__init__(Step, db)
