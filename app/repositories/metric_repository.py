"""
Metric repository - Database operations for metrics
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models import Metric


class MetricRepository:
    """Repository for metric database operations"""
    
    @staticmethod
    def create(
        db: Session,
        response_id: int,
        name: str,
        value: float,
        metadata: Optional[dict] = None
    ) -> Metric:
        """Create a new metric"""
        metric = Metric(
            response_id=response_id,
            name=name,
            value=value,
            metadata_json=metadata
        )
        db.add(metric)
        db.commit()
        db.refresh(metric)
        return metric
    
    @staticmethod
    def create_batch(
        db: Session,
        response_id: int,
        metrics: dict
    ) -> List[Metric]:
        """Create multiple metrics for a response"""
        metric_objects = []
        for metric_name, metric_value in metrics.items():
            metric = Metric(
                response_id=response_id,
                name=metric_name,
                value=metric_value.get("value", 0.0),
                metadata_json=metric_value.get("metadata")
            )
            metric_objects.append(metric)
            db.add(metric)
        db.commit()
        return metric_objects
    
    @staticmethod
    def get_by_response_id(db: Session, response_id: int) -> List[Metric]:
        """Get all metrics for a response"""
        return db.query(Metric).filter(Metric.response_id == response_id).all()
    
    @staticmethod
    def get_by_experiment_id(db: Session, experiment_id: int) -> List[Metric]:
        """Get all metrics for all responses in an experiment"""
        from app.db.models import Response
        return db.query(Metric).join(Response).filter(
            Response.experiment_id == experiment_id
        ).all()
