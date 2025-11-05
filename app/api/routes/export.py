"""
Export API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import csv
import io
import json

from app.db.database import get_db
from app.repositories.experiment_repository import ExperimentRepository
from app.repositories.response_repository import ResponseRepository
from app.repositories.metric_repository import MetricRepository
from app.core.exceptions import raise_experiment_not_found

router = APIRouter()


@router.get("/experiment/{experiment_id}/csv")
async def export_experiment_csv(
    experiment_id: int,
    db: Session = Depends(get_db)
):
    """Export experiment data as CSV"""
    experiment = ExperimentRepository.get_by_id(db, experiment_id)
    if not experiment:
        raise_experiment_not_found(experiment_id)
    
    responses = ResponseRepository.get_by_experiment_id(db, experiment_id)
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Response ID", "Temperature", "Top P", "Max Tokens",
        "Text", "Finish Reason", "Length Score", "Coherence Score",
        "Completeness Score", "Structure Score", "Readability Score",
        "Overall Score"
    ])
    
    # Write data rows
    for response in responses:
        metrics = MetricRepository.get_by_response_id(db, response.id)
        metrics_dict = {m.name: m.value for m in metrics}
        
        writer.writerow([
            response.id,
            response.temperature,
            response.top_p,
            response.max_tokens,
            response.text.replace('\n', ' ').replace('\r', ' '),  # Clean newlines
            response.finish_reason or "",
            metrics_dict.get("length_score", ""),
            metrics_dict.get("coherence_score", ""),
            metrics_dict.get("completeness_score", ""),
            metrics_dict.get("structure_score", ""),
            metrics_dict.get("readability_score", ""),
            metrics_dict.get("overall_score", "")
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=experiment_{experiment_id}.csv"
        }
    )


@router.get("/experiment/{experiment_id}/json")
async def export_experiment_json(
    experiment_id: int,
    db: Session = Depends(get_db)
):
    """Export experiment data as JSON"""
    experiment = ExperimentRepository.get_by_id(db, experiment_id)
    if not experiment:
        raise_experiment_not_found(experiment_id)
    
    responses = ResponseRepository.get_by_experiment_id(db, experiment_id)
    
    # Build JSON structure
    data = {
        "experiment": {
            "id": experiment.id,
            "name": experiment.name,
            "prompt": experiment.prompt,
            "created_at": experiment.created_at.isoformat() if experiment.created_at else None
        },
        "responses": []
    }
    
    for response in responses:
        metrics = MetricRepository.get_by_response_id(db, response.id)
        metrics_dict = {
            m.name: {
                "value": m.value,
                "metadata": m.metadata_json
            }
            for m in metrics
        }
        
        data["responses"].append({
            "id": response.id,
            "temperature": response.temperature,
            "top_p": response.top_p,
            "max_tokens": response.max_tokens,
            "text": response.text,
            "finish_reason": response.finish_reason,
            "created_at": response.created_at.isoformat() if response.created_at else None,
            "metrics": metrics_dict
        })
    
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    
    return StreamingResponse(
        io.BytesIO(json_str.encode('utf-8')),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=experiment_{experiment_id}.json"
        }
    )