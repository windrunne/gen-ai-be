"""
Experiment repository - Database operations for experiments
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models import Experiment, Response
from app.core.constants import DEFAULT_PAGINATION_LIMIT


class ExperimentRepository:
    """Repository for experiment database operations"""
    
    @staticmethod
    def create(db: Session, name: str, prompt: str) -> Experiment:
        """Create a new experiment"""
        experiment = Experiment(name=name, prompt=prompt)
        db.add(experiment)
        db.commit()
        db.refresh(experiment)
        return experiment
    
    @staticmethod
    def get_by_id(db: Session, experiment_id: int) -> Optional[Experiment]:
        """Get experiment by ID"""
        return db.query(Experiment).filter(Experiment.id == experiment_id).first()
    
    @staticmethod
    def get_all(
        db: Session, 
        skip: int = 0, 
        limit: int = DEFAULT_PAGINATION_LIMIT
    ) -> List[Experiment]:
        """Get all experiments with pagination"""
        return db.query(Experiment).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete(db: Session, experiment_id: int) -> bool:
        """Delete an experiment"""
        experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if not experiment:
            return False
        db.delete(experiment)
        db.commit()
        return True
    
    @staticmethod
    def get_response_count(db: Session, experiment_id: int) -> int:
        """Get count of responses for an experiment"""
        return db.query(Response).filter(Response.experiment_id == experiment_id).count()
