"""
Response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class ValidationMetadata(BaseModel):
    """Schema for response validation metadata"""
    is_valid: bool
    is_corrupted: bool
    is_truncated: bool
    corruption_score: float = Field(..., ge=0.0, le=1.0)
    warnings: List[str] = Field(default_factory=list)


class MetricData(BaseModel):
    """Schema for individual metric data"""
    name: str
    value: float
    metadata: Optional[dict] = None


class ResponseWithMetrics(BaseModel):
    """Schema for response with its metrics"""
    id: int
    experiment_id: int
    temperature: float
    top_p: float
    max_tokens: int
    text: str
    finish_reason: Optional[str] = None
    validation_metadata: Optional[ValidationMetadata] = None
    created_at: str
    metrics: List[MetricData]
    
    class Config:
        from_attributes = True
