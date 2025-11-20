from fastapi import APIRouter, Depends, status
from typing import List as TypeList
from app.schemas.project_schema import Project, ProjectCreate, ProjectUpdate, ProjectAddUser, ProjectRemoveUser
from app.schemas.response_schema import ResponseModel
from app.services.project_service import ProjectService
from app.api.dependencies import get_project_service, get_current_user_id

router = APIRouter()

@router.post("/", response_model=ResponseModel[Project], status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    project_service: ProjectService = Depends(get_project_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    new_project = project_service.create_project(project, user_internal_id)
    return ResponseModel(data=new_project, message="Project created successfully")

@router.get("/{project_id}", response_model=ResponseModel[Project])
def get_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    project = project_service.get_project(project_id, user_internal_id)
    return ResponseModel(data=project, message="Project retrieved successfully")

@router.get("/", response_model=ResponseModel[TypeList[Project]])
def get_all_projects(
    project_service: ProjectService = Depends(get_project_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    projects = project_service.get_all_projects_for_user(user_internal_id)
    return ResponseModel(data=projects, message="Projects retrieved successfully")

@router.put("/{project_id}", response_model=ResponseModel[Project])
def update_project(
    project_id: int,
    project: ProjectUpdate,
    project_service: ProjectService = Depends(get_project_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    updated_project = project_service.update_project(project_id, project, user_internal_id)
    return ResponseModel(data=updated_project, message="Project updated successfully")

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    project_service: ProjectService = Depends(get_project_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    project_service.delete_project(project_id, user_internal_id)
    return ResponseModel(message="Project deleted successfully")

@router.post("/{project_id}/users", response_model=ResponseModel[Project])
def add_user_to_project(
    project_id: int,
    user_data: ProjectAddUser,
    project_service: ProjectService = Depends(get_project_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    updated_project = project_service.add_user_to_project(project_id, user_data.user_external_id, user_internal_id)
    return ResponseModel(data=updated_project, message="User added to project successfully")

@router.delete("/{project_id}/users", response_model=ResponseModel[Project])
def remove_user_from_project(
    project_id: int,
    user_data: ProjectRemoveUser,
    project_service: ProjectService = Depends(get_project_service),
    user_internal_id: int = Depends(get_current_user_id)
):
    updated_project = project_service.remove_user_from_project(project_id, user_data.user_external_id, user_internal_id)
    return ResponseModel(data=updated_project, message="User removed from project successfully")
