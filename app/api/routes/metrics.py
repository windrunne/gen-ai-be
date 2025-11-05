"""
Metrics API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.experiment_repository import ExperimentRepository
from app.services.metrics_aggregation_service import MetricsAggregationService
from app.core.exceptions import raise_experiment_not_found

router = APIRouter()


@router.get("/experiment/{experiment_id}/summary")
async def get_experiment_metrics_summary(
    experiment_id: int,
    db: Session = Depends(get_db)
):
    """Get metrics summary for all responses in an experiment"""
    # Verify experiment exists
    experiment = ExperimentRepository.get_by_id(db, experiment_id)
    if not experiment:
        raise_experiment_not_found(experiment_id)
    
    # Get metrics summary
    summary = MetricsAggregationService.get_experiment_metrics_summary(db, experiment_id)
    
    if not summary:
        raise HTTPException(
            status_code=404,
            detail="No responses found for this experiment"
        )
    
    return summary