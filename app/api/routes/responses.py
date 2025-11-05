"""
Responses API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.services.response_service import ResponseService
from app.schemas.response import ResponseWithMetrics
from app.core.exceptions import raise_response_not_found

router = APIRouter()


@router.get("/experiment/{experiment_id}", response_model=List[ResponseWithMetrics])
async def get_experiment_responses(
    experiment_id: int,
    db: Session = Depends(get_db)
):
    """Get all responses for an experiment with their metrics"""
    responses = ResponseService.get_experiment_responses_with_metrics(db, experiment_id)
    return responses


@router.get("/{response_id}", response_model=ResponseWithMetrics)
async def get_response(
    response_id: int,
    db: Session = Depends(get_db)
):
    """Get a single response with its metrics"""
    response = ResponseService.get_response_with_metrics(db, response_id)
    if not response:
        raise_response_not_found(response_id)
    return response