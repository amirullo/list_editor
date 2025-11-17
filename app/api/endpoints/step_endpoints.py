from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.step_service import StepService
from app.schemas.step_schema import Step, StepCreate, StepUpdate
from typing import List

router = APIRouter()

@router.post("/", response_model=Step, status_code=status.HTTP_201_CREATED)
def create_step(step: StepCreate, db: Session = Depends(get_db)):
    return StepService(db).create_step(step)

@router.get("/{step_id}", response_model=Step)
def get_step(step_id: int, db: Session = Depends(get_db)):
    step = StepService(db).get_step(step_id)
    if not step:
        raise HTTPException(status_code=4.04, detail="Step not found")
    return step

@router.get("/", response_model=List[Step])
def get_all_steps(db: Session = Depends(get_db)):
    return StepService(db).get_all_steps()

@router.put("/{step_id}", response_model=Step)
def update_step(step_id: int, step: StepUpdate, db: Session = Depends(get_db)):
    return StepService(db).update_step(step_id, step)

@router.delete("/{step_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_step(step_id: int, db: Session = Depends(get_db)):
    if not StepService(db).delete_step(step_id):
        raise HTTPException(status_code=404, detail="Step not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
