from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.step_service import StepService
from app.schemas.step_schema import Step, StepCreate, StepUpdate
from app.schemas.response_schema import ResponseModel # Import ResponseModel
from typing import List

router = APIRouter()

@router.post("/", response_model=ResponseModel[Step], status_code=status.HTTP_201_CREATED)
def create_step(step: StepCreate, db: Session = Depends(get_db)):
    new_step = StepService(db).create_step(step)
    return ResponseModel(data=new_step, message="Step created successfully")

@router.get("/{step_id}", response_model=ResponseModel[Step])
def get_step(step_id: int, db: Session = Depends(get_db)):
    step = StepService(db).get_step(step_id)
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    return ResponseModel(data=step, message="Step retrieved successfully")

@router.get("/", response_model=ResponseModel[List[Step]])
def get_all_steps(db: Session = Depends(get_db)):
    steps = StepService(db).get_all_steps()
    return ResponseModel(data=steps, message="Steps retrieved successfully")

@router.put("/{step_id}", response_model=ResponseModel[Step])
def update_step(step_id: int, step: StepUpdate, db: Session = Depends(get_db)):
    updated_step = StepService(db).update_step(step_id, step)
    if not updated_step:
        raise HTTPException(status_code=404, detail="Step not found")
    return ResponseModel(data=updated_step, message="Step updated successfully")

@router.delete("/{step_id}", response_model=ResponseModel[dict]) # Changed response_model
def delete_step(step_id: int, db: Session = Depends(get_db)):
    if not StepService(db).delete_step(step_id):
        raise HTTPException(status_code=404, detail="Step not found")
    return ResponseModel(data={"status": "success"}, message="Step deleted successfully") # Wrapped in ResponseModel
