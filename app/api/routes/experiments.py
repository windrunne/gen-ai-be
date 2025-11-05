"""
Experiments API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.repositories.experiment_repository import ExperimentRepository
from app.services.experiment_service import ExperimentService
from app.schemas.experiment import ExperimentCreate, ExperimentResponse, ExperimentDetail
from app.core.exceptions import raise_experiment_not_found
from app.core.constants import DEFAULT_PAGINATION_LIMIT

router = APIRouter()


@router.post("/", response_model=ExperimentResponse)
async def create_experiment(
    experiment_data: ExperimentCreate,
    db: Session = Depends(get_db)
):
    """Create a new experiment and generate responses"""
    try:
        service = ExperimentService()
        result = await service.create_experiment(db, experiment_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating experiment: {str(e)}")


@router.get("/", response_model=List[ExperimentResponse])
async def list_experiments(
    skip: int = 0,
    limit: int = DEFAULT_PAGINATION_LIMIT,
    db: Session = Depends(get_db)
):
    """List all experiments"""
    experiments = ExperimentRepository.get_all(db, skip=skip, limit=limit)
    return [
        {
            "id": exp.id,
            "name": exp.name,
            "prompt": exp.prompt,
            "created_at": exp.created_at.isoformat() if exp.created_at else ""
        }
        for exp in experiments
    ]


@router.get("/{experiment_id}", response_model=ExperimentDetail)
async def get_experiment(
    experiment_id: int,
    db: Session = Depends(get_db)
):
    """Get experiment details"""
    experiment = ExperimentRepository.get_by_id(db, experiment_id)
    if not experiment:
        raise_experiment_not_found(experiment_id)
    
    response_count = ExperimentRepository.get_response_count(db, experiment_id)
    
    return {
        "id": experiment.id,
        "name": experiment.name,
        "prompt": experiment.prompt,
        "created_at": experiment.created_at.isoformat() if experiment.created_at else "",
        "response_count": response_count
    }


@router.delete("/{experiment_id}")
async def delete_experiment(
    experiment_id: int,
    db: Session = Depends(get_db)
):
    """Delete an experiment"""
    success = ExperimentRepository.delete(db, experiment_id)
    if not success:
        raise_experiment_not_found(experiment_id)
    
    return {"message": "Experiment deleted successfully"}