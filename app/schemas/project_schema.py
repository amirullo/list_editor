from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List as TypeList
from datetime import datetime
from .step_schema import Step
from app.models.project_user_model import ProjectRoleType
from app.utils.logger import logger # Import logger

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

class ProjectUser(BaseModel):
    user_external_id: str # Directly map from the SQLAlchemy ProjectUser's user_external_id property
    role_type: ProjectRoleType

    model_config = ConfigDict(from_attributes=True) # Enable mapping from attributes


class Project(ProjectBase):
    id: int
    created_at: datetime # Added created_at
    updated_at: Optional[datetime] = None # Added updated_at
    steps: TypeList['Step'] = []
    project_users: TypeList[ProjectUser] = [] # Renamed from 'participants'

    model_config = ConfigDict(from_attributes=True)

class ProjectAddUser(BaseModel):
    user_external_id: str = Field(..., min_length=1, description="External ID of the user to add")

class ProjectRemoveUser(BaseModel):
    user_external_id: str = Field(..., min_length=1, description="External ID of the user to remove")

Project.model_rebuild()
