from pydantic import BaseModel
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

    class Config:
        from_attributes = True

Project.update_forward_refs()
