"""
Response service - Business logic for responses
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.repositories.response_repository import ResponseRepository
from app.repositories.metric_repository import MetricRepository
from app.schemas.response import ResponseWithMetrics, MetricData, ValidationMetadata


class ResponseService:
    """Service for response business logic"""
    
    
    @staticmethod
    def get_response_with_metrics(db: Session, response_id: int) -> Optional[dict]:
        """Get a single response with its metrics"""
        response = ResponseRepository.get_by_id(db, response_id)
        if not response:
            return None
        
        metrics = MetricRepository.get_by_response_id(db, response_id)
        metrics_data = [
            MetricData(
                name=m.name,
                value=m.value,
                metadata=m.metadata_json
            ).dict()
            for m in metrics
        ]
        
        validation_metadata = None
        if response.validation_metadata:
            validation_metadata = ValidationMetadata(**response.validation_metadata).dict()
        
        return {
            "id": response.id,
            "experiment_id": response.experiment_id,
            "temperature": response.temperature,
            "top_p": response.top_p,
            "max_tokens": response.max_tokens,
            "text": response.text,
            "finish_reason": response.finish_reason,
            "validation_metadata": validation_metadata,
            "created_at": response.created_at.isoformat() if response.created_at else "",
            "metrics": metrics_data
        }
    
    @staticmethod
    def get_experiment_responses_with_metrics(db: Session, experiment_id: int) -> List[dict]:
        """Get all responses for an experiment with their metrics"""
        responses = ResponseRepository.get_by_experiment_id(db, experiment_id)
        
        result = []
        for response in responses:
            metrics = MetricRepository.get_by_response_id(db, response.id)
            metrics_data = [
                MetricData(
                    name=m.name,
                    value=m.value,
                    metadata=m.metadata_json
                ).dict()
                for m in metrics
            ]
            
            validation_metadata = None
            if response.validation_metadata:
                validation_metadata = ValidationMetadata(**response.validation_metadata).dict()
            
            result.append({
                "id": response.id,
                "experiment_id": response.experiment_id,
                "temperature": response.temperature,
                "top_p": response.top_p,
                "max_tokens": response.max_tokens,
                "text": response.text,
                "finish_reason": response.finish_reason,
                "validation_metadata": validation_metadata,
                "created_at": response.created_at.isoformat() if response.created_at else "",
                "metrics": metrics_data
            })
        
        return result
