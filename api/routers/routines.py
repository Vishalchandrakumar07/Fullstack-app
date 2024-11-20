from pydantic import BaseModel
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import joinedload, Session
from api.models import Workout, Routine
from api.deps import db_dependency, user_dependency

router = APIRouter(prefix="/routines", tags=["routines"])


# Base model for Routine
class RoutineBase(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True  # Enable compatibility with ORM models


# Model for creating a new Routine
class RoutineCreate(BaseModel):
    name: str
    description: Optional[str] = None
    workouts: List[int] = []  # List of workout IDs


# Response model for listing routines with workouts
class RoutineResponse(RoutineBase):
    workouts: List[Workout]  # Replace `Workout` with its Pydantic schema if available


# Get all routines for the current user
@router.get("/", response_model=List[RoutineResponse])
def get_routines(
    db: Session = Depends(db_dependency), user: dict = Depends(user_dependency)
):
    routines = (
        db.query(Routine)
        .options(joinedload(Routine.workouts))  # Preload workouts relationship
        .filter(Routine.user_id == user.get("id"))
        .all()
    )
    return routines


# Create a new routine
@router.post("/", response_model=RoutineResponse)
def create_routine(
    routine: RoutineCreate,
    db: Session = Depends(db_dependency),
    user: dict = Depends(user_dependency),
):
    # Create a new Routine instance
    db_routine = Routine(
        name=routine.name, description=routine.description, user_id=user.get("id")
    )

    # Validate and append workouts
    for workout_id in routine.workouts:
        workout = db.query(Workout).filter(Workout.id == workout_id).first()
        if not workout:
            raise HTTPException(
                status_code=404, detail=f"Workout with ID {workout_id} not found"
            )
        db_routine.workouts.append(workout)

    db.add(db_routine)
    db.commit()
    db.refresh(db_routine)  # Refresh to get updated values from the database
    return db_routine


# Delete a routine by ID
@router.delete("/{routine_id}", response_model=RoutineBase)
def delete_routine(
    routine_id: int,
    db: Session = Depends(db_dependency),
    user: dict = Depends(user_dependency),
):
    db_routine = (
        db.query(Routine)
        .filter(Routine.id == routine_id, Routine.user_id == user.get("id"))
        .first()
    )
    if not db_routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    db.delete(db_routine)
    db.commit()
    return db_routine
