"""
Response repository - Database operations for responses
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models import Response


class ResponseRepository:
    """Repository for response database operations"""
    
    @staticmethod
    def create(
        db: Session,
        experiment_id: int,
        temperature: float,
        top_p: float,
        max_tokens: int,
        text: str,
        finish_reason: str,
        validation_metadata: Optional[dict] = None
    ) -> Response:
        """Create a new response"""
        response = Response(
            experiment_id=experiment_id,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            text=text,
            finish_reason=finish_reason,
            validation_metadata=validation_metadata
        )
        db.add(response)
        db.commit()
        db.refresh(response)
        return response
    
    @staticmethod
    def get_by_id(db: Session, response_id: int) -> Optional[Response]:
        """Get response by ID"""
        return db.query(Response).filter(Response.id == response_id).first()
    
    @staticmethod
    def get_by_experiment_id(db: Session, experiment_id: int) -> List[Response]:
        """Get all responses for an experiment"""
        return db.query(Response).filter(Response.experiment_id == experiment_id).all()
    
    @staticmethod
    def get_all_for_metrics_summary(db: Session, experiment_id: int) -> List[Response]:
        """Get all responses for an experiment (optimized for metrics summary)"""
        return db.query(Response).filter(Response.experiment_id == experiment_id).all()
