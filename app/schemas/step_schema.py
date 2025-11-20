from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class StepBase(BaseModel):
    name: str
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    materials_price: Optional[float] = None
    workers_price: Optional[float] = None
    project_id: int
    parent_step_id: Optional[int] = None

class StepCreate(StepBase):
    pass

class StepUpdate(StepBase):
    pass

class Step(StepBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    sub_steps: List['Step'] = []

    model_config = ConfigDict(from_attributes=True)

Step.model_rebuild()
