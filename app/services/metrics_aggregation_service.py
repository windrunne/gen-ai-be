"""
Metrics Aggregation Service - Aggregates stored metrics from database
"""
import statistics
from sqlalchemy.orm import Session
from typing import Dict, List
from app.repositories.response_repository import ResponseRepository
from app.repositories.metric_repository import MetricRepository


class MetricsAggregationService:
    """Service for aggregating stored metrics and calculating summary statistics"""
    
    @staticmethod
    def get_experiment_metrics_summary(db: Session, experiment_id: int) -> Dict[str, dict]:
        """
        Get aggregated metrics summary for an experiment
        
        Args:
            db: Database session
            experiment_id: ID of the experiment
            
        Returns:
            Dictionary mapping metric names to summary statistics
        """
        responses = ResponseRepository.get_all_for_metrics_summary(db, experiment_id)
        
        if not responses:
            return {}
        
        # Aggregate metrics by name
        metrics_summary: Dict[str, Dict[str, List]] = {}
        
        for response in responses:
            metrics = MetricRepository.get_by_response_id(db, response.id)
            
            for metric in metrics:
                if metric.name not in metrics_summary:
                    metrics_summary[metric.name] = {
                        "values": [],
                        "responses": []
                    }
                
                metrics_summary[metric.name]["values"].append(metric.value)
                metrics_summary[metric.name]["responses"].append({
                    "response_id": response.id,
                    "temperature": response.temperature,
                    "top_p": response.top_p,
                    "value": metric.value
                })
        
        # Calculate statistics
        summary = {}
        for metric_name, data in metrics_summary.items():
            values = data["values"]
            summary[metric_name] = {
                "mean": statistics.mean(values) if values else 0,
                "median": statistics.median(values) if values else 0,
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
                "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                "count": len(values),
                "responses": data["responses"]
            }
        
        return summary