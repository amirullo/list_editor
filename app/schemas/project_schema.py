from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from .step_schema import Step

class ProjectBase(BaseModel):
    name: str
    place_description: Optional[str] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    total_materials_price: Optional[float] = None
    total_workers_price: Optional[float] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    steps: List['Step'] = []

    model_config = ConfigDict(from_attributes=True)

Project.model_rebuild()
